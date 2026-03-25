import os
import logging
import http.client
import pandas as pd
import sqlite3

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool

from src.config import employee_db_path
from src.schema import (FindUserInformation, FindEmployeeInformation, FindEmployeeEmail,
                        FindEmployeeId, SearchQuery)
from src.custom_exceptions import (LoanDetailsExceptionError, EmployeeDetailsExceptionError,
                                   UserDetailsExceptionError, APIExcpetionError,
                                   SearchToolExceptionError)

logger=logging.getLogger("Agent_Tools")

# -------------------- Tools -------------------- #

@tool
def find_loan_details() -> str:
    """find the loan information or details asked by user"""
    logger.info("Starting loan details retrieval from file.")

    try:
        with open("stories/loan.txt", "r+", encoding="utf-8") as f:
            loan_details = f.read()
            logger.info("Successfully read loan details from file.")
            return loan_details

    except FileNotFoundError:
        logger.exception("Loan file not found at path: stories/loan.txt")
        raise LoanDetailsExceptionError(
            "No such file or directory, unable to find the loan document."
        )

    except Exception as e:
        logger.exception("Unexpected error while reading loan document.")
        raise LoanDetailsExceptionError(
            "Something went wrong while reading loan document. Please check logs."
        )


@tool(args_schema=FindUserInformation)
def find_user_information(name: str) -> list:
    """find user information by name"""
    logger.info(f"Fetching user information for name: {name}")

    try:
        df = pd.read_csv("users_info.csv")
        logger.info("User CSV file loaded successfully.")

        result = df[df["user_name"] == name].to_dict(orient="records")

        if not result:
            logger.warning(f"No user found with name: {name}")
        else:
            logger.info(f"User information retrieved successfully for: {name}")

        return result

    except FileNotFoundError:
        logger.exception("User info CSV file not found: users_info.csv")
        raise UserDetailsExceptionError(
            "No such file or directory, unable to find the user info csv document"
        )

    except Exception as e:
        logger.exception(f"Error while retrieving user information for name: {name}")
        raise UserDetailsExceptionError(
            "Something went wrong while reading user document. Please check logs."
        )


@tool(args_schema=FindEmployeeInformation)
def find_employee_information(name: str) -> list | str:
    """Find employee information/details/info by name"""
    logger.info(f"Fetching employee information for name: {name}")

    try:
        with sqlite3.connect(employee_db_path) as connection:
            cursor = connection.cursor()

            logger.info("Executing query for employee information.")
            cursor.execute("SELECT * FROM emp WHERE name=?", (name,))
            emp_info = cursor.fetchall()

            if not emp_info:
                logger.warning(f"No employee found with name: {name}")
                return "No employee found."

            private_data = bool(emp_info[0][3])

            if private_data:
                logger.warning(f"Access denied for employee {name} due to private data.")
                result = "Can't provide the user information, because it is private data."
            else:
                logger.info(f"Employee information retrieved successfully for: {name}")
                result = emp_info

            return result

    except sqlite3.Error as e:
        logger.exception(f"Database error while retrieving employee info: {e}")
        raise EmployeeDetailsExceptionError(
            "Issue with retrieving records from the database/table"
        )

    except Exception as e:
        logger.exception(f"Unexpected error while fetching employee info for {name}")
        raise EmployeeDetailsExceptionError(
            "Something went wrong while reading employee information from the database. Please check logs."
        )


@tool(args_schema=FindEmployeeEmail)
def find_employee_email(name: str) -> str:
    """find employee email id by name"""
    logger.info(f"Fetching employee email for name: {name}")

    try:
        with sqlite3.connect(employee_db_path) as connection:
            cursor = connection.cursor()

            logger.info("Executing query for employee email.")
            cursor.execute("SELECT email FROM emp WHERE name=?", (name,))
            result = cursor.fetchall()

            if not result:
                logger.warning(f"No email found for employee: {name}")
                return "No email found."

            email = result[0][0]
            logger.info(f"Email retrieved successfully for employee: {name}")

            return email

    except sqlite3.Error as e:
        logger.exception(f"Database error while retrieving employee email: {e}")
        raise EmployeeDetailsExceptionError(
            "Issue with retrieving records from the database/table"
        )

    except Exception as e:
        logger.exception(f"Unexpected error while fetching employee email for {name}")
        raise EmployeeDetailsExceptionError(
            "Something went wrong while reading employee email. Please check logs."
        )

@tool(args_schema=FindEmployeeId)

def find_employee_id(name: str) -> int:
    """Find employee id by name
    return:
    int:employee id"""
    try:
        logger.info("Initiated find_employee_id().")
        with sqlite3.connect(employee_db_path) as connection:
            cursor = connection.cursor()
            logger.info("successfully setup the DB connection")
            cursor.execute("Select id from emp where name=?", (name,))
            logger.info("Done with the execution of query : Select id from emp where name={}"
                        .format(name))
            emp_id = cursor.fetchall()[0][0]
            logger.info("successfully fetched emp_id and returned")
            return emp_id
    except sqlite3.Error:
        logger.exception("Something went wrong while fetching employee id.")
        raise EmployeeDetailsExceptionError("Issue with retrieving records from the database/table."
                                            " Please check logs.")
    except Exception:
        logger.exception("Something went wrong while fetching employee id.")
        raise EmployeeDetailsExceptionError("something went wrong while reading employee id."
                                            " Please check logs.")

@tool
def credit_tool() -> str:
    """credit tool is a tool which provide information about credit or loan approvals
    return:
    JSON:credit result"""

    try:
        logger.info("Initiated credit_tool().")
        rapidapi_key = os.getenv("RAPIDAPI")
        logger.info("Got the rapidapi key.")
        conn = http.client.HTTPSConnection("credilink-api.p.rapidapi.com")
        logger.info("Successfully created the hhtp connection with webiste credlink.com")

        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': "credilink-api.p.rapidapi.com"
        }
        logger.info("successfully defined the headers for the http connections")
        conn.request("GET", "/records/?page=1&page_size=2", headers=headers)
        logger.info("successfully made the GET request.")

        res = conn.getresponse()
        logger.info("successfully retrieved the http response.")
        data = res.read()
        return data.decode("utf-8")
    except http.client.HTTPException:
        logger.exception("Something went wrong while creating the hhtp connection.")
        raise APIExcpetionError("facing connection issue with rapidapi call. Please check logs.")
    except Exception:
        logger.exception("Something went wrong while creating the hhtp connection.")
        raise APIExcpetionError("Something went wrong while accessing 3rd party credit api call."
                                "Please check logs.")


@tool(args_schema=SearchQuery)
def search_tool(user_query: str) -> str:
    """search tool which search the user query over internet and return the results.
    return:
    str:search result"""
    try:
        logger.info("Initiated search_tool().")
        search = DuckDuckGoSearchRun()
        logger.info("Successfully initiated duckduckgo search engine.")
        return search.invoke(input=user_query)
    except Exception as err:
        logger.exception(err)
        raise SearchToolExceptionError("Something went wrong with search engine. Please check logs.")