from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from pydantic import BaseModel, Field
import http.client
import os
from typing import Dict, Any
import sqlite3
import pandas as pd



def old_code():
    load_dotenv()

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

    @tool
    def find_loan_details()->str:
        """find the loan information or details asked by user
        return:
        str:loan information or details asked by user"""
        with open("/Users/manohharswarna/Desktop/Agent/stories/loan.txt","r+",encoding="utf-8") as f:
            loan_details=f.read()
        return loan_details

    @tool(args_schema=FindUserInformation)
    def find_user_information(name: str) -> list:
        """find user information by name
        return:
        list:user information"""
        df=pd.read_csv("users_info.csv")
        return df[df["user_name"]==name].to_dict(orient="records")

    @tool(args_schema=FindEmployeeInformation)
    def find_employee_information(name: str) -> list[tuple[(int,str)]] | str:
        """Find employee information/details/info by name
        return:
        list[tuple[(int,str)]] | str:employee information"""
        connection = sqlite3.connect("employe.db")
        cursor = connection.cursor()
        cursor.execute("Select * from emp where name=?",(name,))
        emp_info=cursor.fetchall()
        private_data=bool(emp_info[0][3])
        if private_data:
            result="Can't provide the user information, because it is private data."
        else:
            result=emp_info
        connection.close()
        return result

    @tool(args_schema=FindEmployeeEmail)
    def find_employee_email(name: str) -> str:
        """find employee email id by name
        return:
        str:email"""
        connection = sqlite3.connect("employe.db")
        cursor = connection.cursor()
        cursor.execute("Select email from emp where name=?", (name,))
        email = cursor.fetchall()[0][0]
        connection.close()
        return email

    @tool(args_schema=FindEmployeeId)
    def find_employee_id(name: str) -> int:
        """Find employee id by name
        return:
        int:employee id"""
        connection = sqlite3.connect("employe.db")
        cursor = connection.cursor()
        cursor.execute("Select id from emp where name=?",(name,))
        emp_id=cursor.fetchall()[0][0]
        connection.close()
        return emp_id

    @tool
    def credit_tool() -> Dict[str, Any]:
        """credit tool is a tool which provide information about credit or loan approvals
        return:
        JSON:credit result"""

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

    @tool(args_schema=SearchQuery)
    def search_tool(user_query: str) -> str:
        """search tool which search the user query over internet and return the results.
        return:
        str:search result"""

        search = DuckDuckGoSearchRun()
        return search.invoke(input=user_query)


    def get_chat_records_count(cursor) -> int:
        cursor.execute("select COUNT(*) from chatbot_history LIMIT 5")
        return cursor.fetchall()[0][0]

    llm = ChatOpenAI(model="gpt-4o")
    tools=[search_tool,credit_tool,find_employee_information,find_employee_email,find_employee_id,find_user_information,find_loan_details]
    agent = create_agent(llm,tools=tools)

    '''result = agent.invoke({"messages":[SystemMessage(content="Think that You are helpful banking assistant"),
                                      HumanMessage(content="Hello how are you today")]})'''
    messages=[SystemMessage(content="""Think that You are helpful banking assistant and bank name is ABCD.
    Your response to the user questions should be in banking tone.
    If user ask anything about account balance check, just provide the random number with $ currency symbol.
    """)]
    messages1 = [SystemMessage(content="""Think that You are helpful banking assistant and bank name is ABCD.
        Your response to the user questions should be in banking tone.
        If user ask anything about account balance check, just provide the random number with $ currency symbol.
        """)]

    #print(result["messages"][-1].content)

    ## Welcome message

    print("""Welcome to the ABCD Bank chatbot v0.0.1
    I can help you with all your questions!""")

    user_name=input("Bot : Please enter your name: ").strip()

    if user_name.lower() == "no":
        messages.append(HumanMessage(content="Greet user with unique greeting message"))
        greet_response=agent.invoke({"messages":messages})
        #messages.append(AIMessage(content=greet_response["messages"][-1].content))
        print("Bot : {}".format(greet_response["messages"][-1].content))
    else:
        messages.append(HumanMessage(content="Hello"))
        greet_response=agent.invoke({"messages":messages})
        #messages.append(AIMessage(content=greet_response["messages"][-1].content))
        print("Bot :{}, {}".format(user_name,greet_response["messages"][-1].content))

    connection = sqlite3.connect("chatbot_conversation.db")
    cursor = connection.cursor()

    chatbot_record_count=get_chat_records_count(cursor)

    if chatbot_record_count==0:
        print("+"*80)
        print("zero records found")
        print("+"*80)

        user_input = str(input("user :")).strip()
        print("\n")
        if user_input.lower() in ["exit", "quit"]:
            messages.append(HumanMessage(content="provide unique goodbye message to user."))
            goodbye_response = agent.invoke({"messages": messages})
            messages.append(AIMessage(content=goodbye_response["messages"][-1].content))
            print("Bot : {}".format(goodbye_response["messages"][-1].content))
        else:
            messages.append(HumanMessage(content=user_input))
            response = agent.invoke({"messages": messages})
            #messages.append(AIMessage(content=response["messages"][-1].content))
            print("Bot : {}".format(response["messages"][-1].content))
            cursor.execute("""INSERT INTO chatbot_history (user_query, bot_response) VALUES (?, ?)""", (user_input, response["messages"][-1].content))


    while True:
        messages1 = [SystemMessage(content="""Think that You are helpful banking assistant and bank name is ABCD.
                Your response to the user questions should be in banking tone.
                If user ask anything about account balance check, just provide the random number with $ currency symbol.
                """)]
        user_input = str(input("user :")).strip()
        print("\n")
        if user_input.lower() in ["exit","quit"]:
            messages.append(HumanMessage(content="provide unique goodbye message to user."))
            goodbye_response=agent.invoke({"messages":messages})
            messages.append(AIMessage(content=goodbye_response["messages"][-1].content))
            print("Bot : {}".format(goodbye_response["messages"][-1].content))
            break
        cursor.execute("""select * from chatbot_history LIMIT 10""")
        conversation_history = cursor.fetchall()
        for conv in conversation_history:
            messages1.append(HumanMessage(content=conv[0]))
            messages1.append(AIMessage(content=conv[1]))

        messages1.append(HumanMessage(content=user_input))
        response = agent.invoke({"messages": messages1})
        #messages.append(AIMessage(content=response["messages"][-1].content))
        print("Bot : {}".format(response["messages"][-1].content))
        cursor.execute("""INSERT INTO chatbot_history (user_query, bot_response)
                          VALUES (?, ?)""", (user_input, response["messages"][-1].content))

    connection.commit()
    connection.close()
        

    '''while True:
        user_input = str(input("user :")).strip()
        print("\n")
        if user_input.lower() in ["exit","quit"]:
            messages.append(HumanMessage(content="provide unique goodbye message to user."))
            goodbye_response=agent.invoke({"messages":messages})
            messages.append(AIMessage(content=goodbye_response["messages"][-1].content))
            print("Bot : {}".format(goodbye_response["messages"][-1].content))
            break
        messages.append(HumanMessage(content=user_input))
        response=agent.invoke({"messages":messages})
        messages.append(AIMessage(content=response["messages"][-1].content))
        print("Bot : {}".format(response["messages"][-1].content))

    print('+'*80)
    print(messages)
    print('+'*80)


    ### saving conversations
    with open("/Users/manohharswarna/Desktop/Agent/conversations/{}.txt".format(datetime.now().strftime("%Y%m%d-%H%M%S")),mode="w+", encoding="utf-8") as f:
        for msg in messages:
            f.write(msg.content + "\n")

    print('-'*50)
    for i in messages:
        print("message: {}".format(i.content))'''



if __name__=="__main__":
    #new_code()
    old_code()