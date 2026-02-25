import http.client
import os
import sqlite3
from typing import Any, Dict, List, Tuple

import pandas as pd
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.config import employee_db_path,chatbot_conversation_db_path



system_prompt="""
Think that you are a helpful banking assistant.
Bank name is ABCD.
Use a professional banking tone.
If the user asks about account balance, return a random $ amount.
if user ask any questions other than banking, by letting user know with polite response,
can't provide responses to the questions other thank baking related. 
"""

# -------------------- Pydantic Schemas -------------------- #

class FindEmployeeInformation(BaseModel):
    """Input for the finding employee information queries"""
    name: str = Field(description="name of the employee")


class FindEmployeeEmail(BaseModel):
    """Input for finding employee email id """
    name: str = Field(description="name of the employee")


class FindEmployeeId(BaseModel):
    """Input for the finding employee id queries"""
    name: str = Field(description="name of the employee")


class SearchQuery(BaseModel):
    """Input for search query"""
    user_query: str = Field(description="what is the user query to search for")


class FindUserInformation(BaseModel):
    """Input for finding user information queries"""
    name: str = Field(description="name of the user")

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



# -------------------- Utilities -------------------- #

def get_chat_records_count(cursor) -> int|str:
    try:
        cursor.execute("select COUNT(*) from chatbot_history LIMIT 5")
        return cursor.fetchall()[0][0]
    except sqlite3.Error as e:
        return "facing isssue while retriving records from the database/table"


# -------------------- Main App -------------------- #

def main()->None:
    try:
        load_dotenv()
        llm = ChatOpenAI(model="gpt-4o")
        tools = [search_tool,
                 credit_tool,
                 find_employee_information,
                 find_employee_email,
                 find_employee_id,
                 find_user_information,
                 find_loan_details]
        agent = create_agent(llm, tools=tools)
        base_llm_message = [SystemMessage(content=system_prompt)]
        loop_chat_llm_message= [SystemMessage(content=system_prompt)]

        #Chatbot welcome message.
        print("""
             \tWelcome to the ABCD Bank chatbot v0.0.1
             \tI can help you with all your questions!\n""")

        #Taking user name as input
        user_name = input("Bot : Please enter your name: ").strip()
        try:
            if user_name.lower() == "no":
                base_llm_message.append(HumanMessage(content="Greet user with unique greeting message"))
                greet_response = agent.invoke({"messages": base_llm_message})
                # messages.append(AIMessage(content=greet_response["messages"][-1].content))
                print("Bot : {}".format(greet_response["messages"][-1].content))
            else:
                base_llm_message.append(HumanMessage(content="Hello"))
                greet_response = agent.invoke({"messages": base_llm_message})
                # messages.append(AIMessage(content=greet_response["messages"][-1].content))
                print("Bot :{}, {}".format(user_name, greet_response["messages"][-1].content))
        except Exception as e:
            print("Unable to greet user with unique greeting message, due to the exception occured")
        try:
            #reading last 10 chatbot conversation from the database
            with sqlite3.connect(chatbot_conversation_db_path) as connection:
                cursor = connection.cursor()
                chatbot_record_count = get_chat_records_count(cursor)
                if chatbot_record_count == 0:
                    user_input = str(input("user :")).strip()
                    print("\n")
                    if user_input.lower() in ["exit", "quit"]:
                        base_llm_message.append(HumanMessage(content="provide unique goodbye message to user."))
                        goodbye_response = agent.invoke({"messages": base_llm_message})
                        base_llm_message.append(AIMessage(content=goodbye_response["messages"][-1].content))
                        print("Bot : {}".format(goodbye_response["messages"][-1].content))
                    else:
                        base_llm_message.append(HumanMessage(content=user_input))
                        response = agent.invoke({"messages": base_llm_message})
                        # messages.append(AIMessage(content=response["messages"][-1].content))
                        print("Bot : {}".format(response["messages"][-1].content))
                        cursor.execute("""
                                       INSERT INTO chatbot_history (user_query, bot_response)
                                       VALUES (?, ?)""", (user_input,
                                       response["messages"][-1].content)
                                       )

                #loop chatbot logic
                while True:
                    user_input = str(input("user :")).strip()
                    print("\n")
                    if user_input.lower() in ["exit", "quit"]:
                        base_llm_message.append(HumanMessage(content="provide unique goodbye message to user."))
                        goodbye_response = agent.invoke({"messages": base_llm_message})
                        base_llm_message.append(AIMessage(content=goodbye_response["messages"][-1].content))
                        print("Bot : {}".format(goodbye_response["messages"][-1].content))
                        break
                    cursor.execute("""
                                   select user_query,bot_response from
                                   (select ROWID, * from chatbot_history ORDER by ROWID DESC LIMIT 5) as pr 
                                   ORDER by pr.ROWID DESC
                                   """)
                    conversation_history = cursor.fetchall()
                    for conv in conversation_history:
                        loop_chat_llm_message.append(HumanMessage(content=conv[0]))
                        loop_chat_llm_message.append(AIMessage(content=conv[1]))

                    loop_chat_llm_message.append(HumanMessage(content=user_input))
                    response = agent.invoke({"messages": loop_chat_llm_message})
                    # messages.append(AIMessage(content=response["messages"][-1].content))
                    print("Bot : {}".format(response["messages"][-1].content))
                    cursor.execute("""
                                   INSERT INTO chatbot_history (user_query, bot_response)
                                   VALUES (?, ?)""", (user_input, response["messages"][-1].content)
                                   )
        except Exception as e:
            print("Exception : {}".format(e))
    except Exception as e:
        print("Exception : {}".format(e))
    finally:
        print("+"*80)
        print("execution completed")
        print("+"*80)


if __name__ == "__main__":
    main()