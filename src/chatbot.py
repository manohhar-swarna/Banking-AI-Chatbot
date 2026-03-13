import sqlite3

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.prompt import system_prompt
from src.utility import get_chat_records_count
from src.config import chatbot_conversation_db_path
from src.tools import (search_tool, credit_tool, find_employee_information, find_employee_email,
                 find_employee_id, find_user_information, find_loan_details)

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