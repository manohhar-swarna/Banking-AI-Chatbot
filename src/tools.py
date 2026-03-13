import os
import http.client
import pandas as pd
import sqlite3
from typing import Any, Dict, List, Tuple

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool

from src.schema import (FindUserInformation, FindEmployeeInformation, FindEmployeeEmail,
                        FindEmployeeId, SearchQuery)
from src.config import employee_db_path


# -------------------- Tools -------------------- #

@tool
def find_loan_details() -> str:
    """find the loan information or details asked by user
    return:
    str:loan information or details asked by user"""
    try:
        with open("stories/loan.txt", "r+", encoding="utf-8") as f:
            loan_details = f.read()
            return loan_details
    except FileNotFoundError as e:
        return "unable to find the loan document"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))


@tool(args_schema=FindUserInformation)
def find_user_information(name: str) -> list:
    """find user information by name
    return:
    list:user information"""
    try:
        df = pd.read_csv("users_info.csv")
        return df[df["user_name"] == name].to_dict(orient="records")
    except FileNotFoundError as e:
        return "unable to find the user info csv document"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))
    except Exception as e:
        return "there no user_name column in the dataframe"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))

@tool(args_schema=FindEmployeeInformation)
def find_employee_information(name: str) -> list[tuple[(int, str)]] | str:
    """Find employee information/details/info by name
    return:
    list[tuple[(int,str)]] | str:employee information"""
    try:
        with sqlite3.connect(employee_db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("Select * from emp where name=?", (name,))
            emp_info = cursor.fetchall()
            private_data = bool(emp_info[0][3])
            if private_data:
                result = "Can't provide the user information, because it is private data."
            else:
                result = emp_info
            return result
    except sqlite3.Error as e:
        return "Issue with retriving records from the database/table"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))

@tool(args_schema=FindEmployeeEmail)
def find_employee_email(name: str) -> str:
    """find employee email id by name
    return:
    str:email"""
    try:
        with sqlite3.connect(employee_db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("Select email from emp where name=?", (name,))
            email = cursor.fetchall()[0][0]
            return email
    except sqlite3.Error as e:
        return "Issue with retriving records from the database/table"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))

@tool(args_schema=FindEmployeeId)
def find_employee_id(name: str) -> int:
    """Find employee id by name
    return:
    int:employee id"""
    try:
        with sqlite3.connect(employee_db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("Select id from emp where name=?", (name,))
            emp_id = cursor.fetchall()[0][0]
            return emp_id
    except sqlite3.Error as e:
        return "Issue with retriving records from the database/table"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))

@tool
def credit_tool() -> Dict[str, Any]:
    """credit tool is a tool which provide information about credit or loan approvals
    return:
    JSON:credit result"""

    try:
        rapidapi_key = os.getenv("RAPIDAPI")
        conn = http.client.HTTPSConnection("credilink-api.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': "credilink-api.p.rapidapi.com"
        }

        conn.request("GET", "/records/?page=1&page_size=2", headers=headers)

        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")
    except http.client.HTTPException as e:
        return "facing connection issue with rapidapi call"
        #print("Type of Exception : {}".format(type(e)))
        #print("Exception message : {}".format(e))

@tool(args_schema=SearchQuery)
def search_tool(user_query: str) -> str:
    """search tool which search the user query over internet and return the results.
    return:
    str:search result"""
    try:
        search = DuckDuckGoSearchRun()
        return search.invoke(input=user_query)
    except Exception as e:
        return "facing issuing in web searching"