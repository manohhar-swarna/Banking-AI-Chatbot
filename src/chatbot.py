import sqlite3
import logging

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.log import setup_logging
from src.custom_exceptions import ChatbotExceptionError,ChathistoryCountExceptionError
from src.prompt import system_prompt
from src.utility import get_chat_records_count
from src.config import chatbot_conversation_db_path
from src.tools import (search_tool, credit_tool, find_employee_information, find_employee_email,
                 find_employee_id, find_user_information, find_loan_details)


def get_agent():
    logger.info("Starting agent creation process.")
    try:
        load_dotenv()
        logger.info("Environment variables loaded successfully.")

        llm = ChatOpenAI(model="gpt-4o")
        logger.info("LLM initialized with model gpt-4o.")

        tools = [
            search_tool,
            credit_tool,
            find_employee_information,
            find_employee_email,
            find_employee_id,
            find_user_information,
            find_loan_details,
        ]
        logger.info("Tools configured successfully.")

        agent = create_agent(llm, tools=tools)
        logger.info("Agent created successfully.")

        return agent

    except Exception:
        logger.exception("Error occurred while creating agent.")
        raise ChatbotExceptionError(
            "Something went wrong while creating agent.Please check logs"
        )


def get_greetings(user_name: str, agent) -> str:
    """This method is responsible for getting the greeting for the user"""
    logger.info(f"Generating greeting for user: {user_name}")

    try:
        if user_name.lower() == "no":
            logger.info("User opted for generic greeting.")

            base_llm_message.append(
                HumanMessage(content="Greet user with unique greeting message")
            )

            greet_response = agent.invoke({"messages": base_llm_message})
            greetings = "Bot : {}".format(
                greet_response["messages"][-1].content
            )

            logger.info("Generated generic greeting successfully.")
            return greetings

        else:
            logger.info("User provided name, generating personalized greeting.")

            base_llm_message.append(HumanMessage(content="Hello"))
            greet_response = agent.invoke({"messages": base_llm_message})

            greetings = "Bot :{}, {}".format(
                user_name, greet_response["messages"][-1].content
            )

            logger.info("Generated personalized greeting successfully.")
            return greetings

    except Exception:
        logger.exception("Error occurred while generating greeting.")
        greetings = (
            "Unable to greet user with unique greeting message, due to the exception occurred"
        )
        return greetings


def startup_chatbot(agent) -> None:
    """This method is responsible for starting the chatbot by checking the condition(
    chatbot conversation history count) and set up the chatbot conversation history
    for the loop chatbot."""
    logger.info("Starting chatbot initialization flow.")

    try:
        with sqlite3.connect(chatbot_conversation_db_path) as connection:
            logger.info("Database connection established for startup flow.")

            cursor = connection.cursor()
            chatbot_record_count = get_chat_records_count(cursor)

            logger.info(f"Chatbot history record count: {chatbot_record_count}")

            if chatbot_record_count == 0:
                logger.info("No previous chat history found. Starting fresh session.")

                user_input = str(input("user :")).strip()
                logger.info(f"User input received: {user_input}")

                print("\n")

                if user_input.lower() in ["exit", "quit"]:
                    logger.info("User requested exit during startup.")

                    base_llm_message.append(
                        HumanMessage(
                            content="provide unique goodbye message to user."
                        )
                    )

                    goodbye_response = agent.invoke(
                        {"messages": base_llm_message}
                    )

                    base_llm_message.append(
                        AIMessage(
                            content=goodbye_response["messages"][-1].content
                        )
                    )

                    print(
                        "Bot : {}".format(
                            goodbye_response["messages"][-1].content
                        )
                    )

                else:
                    base_llm_message.append(
                        HumanMessage(content=user_input)
                    )

                    response = agent.invoke(
                        {"messages": base_llm_message}
                    )

                    print(
                        "Bot : {}".format(
                            response["messages"][-1].content
                        )
                    )

                    logger.info("Storing first conversation into database.")

                    cursor.execute(
                        """
                        INSERT INTO chatbot_history (user_query, bot_response)
                        VALUES (?, ?)
                        """,
                        (user_input, response["messages"][-1].content),
                    )

    except sqlite3.Error:
        logger.exception("Database error during startup chatbot.")
        raise ChatbotExceptionError(
            "Something went wrong with database/connections.please check logs."
        )

    except ChathistoryCountExceptionError as e:
        logger.exception("Error while fetching chat history count.")
        raise ChatbotExceptionError(e)

    except Exception:
        logger.exception("Unexpected error during startup chatbot.")
        raise ChatbotExceptionError(
            "Something went wrong while performing startup chatbot.Please check logs"
        )


def loop_chatbot(agent) -> None:
    """This method is responsible for performing multi conversation chatbot"""
    logger.info("Starting chatbot loop for multi-conversation.")

    try:
        with sqlite3.connect(chatbot_conversation_db_path) as connection:
            logger.info("Database connection established for chatbot loop.")

            cursor = connection.cursor()

            while True:
                user_input = str(input("user :")).strip()
                logger.info(f"User input received: {user_input}")

                print("\n")

                if user_input.lower() in ["exit", "quit"]:
                    logger.info("User requested exit from chatbot loop.")

                    base_llm_message.append(
                        HumanMessage(
                            content="provide unique goodbye message to user."
                        )
                    )

                    goodbye_response = agent.invoke(
                        {"messages": base_llm_message}
                    )

                    base_llm_message.append(
                        AIMessage(
                            content=goodbye_response["messages"][-1].content
                        )
                    )

                    print(
                        "Bot : {}".format(
                            goodbye_response["messages"][-1].content
                        )
                    )

                    break

                logger.info("Fetching last 5 conversation history records.")

                cursor.execute(
                    """
                    select user_query,bot_response from
                    (select ROWID, * from chatbot_history ORDER by ROWID DESC LIMIT 5) as pr 
                    ORDER by pr.ROWID DESC
                    """
                )

                conversation_history = cursor.fetchall()
                logger.info(
                    f"Retrieved {len(conversation_history)} past conversation records."
                )

                for conv in conversation_history:
                    loop_chat_llm_message.append(
                        HumanMessage(content=conv[0])
                    )
                    loop_chat_llm_message.append(
                        AIMessage(content=conv[1])
                    )

                loop_chat_llm_message.append(
                    HumanMessage(content=user_input)
                )

                response = agent.invoke(
                    {"messages": loop_chat_llm_message}
                )

                print(
                    "Bot : {}".format(
                        response["messages"][-1].content
                    )
                )

                logger.info("Storing conversation into database.")

                cursor.execute(
                    """
                    INSERT INTO chatbot_history (user_query, bot_response)
                    VALUES (?, ?)
                    """,
                    (user_input, response["messages"][-1].content),
                )

    except sqlite3.Error:
        logger.exception("Database error during chatbot loop.")
        raise ChatbotExceptionError(
            "Something went wrong with database/connections.please check logs."
        )

    except Exception:
        logger.exception("Unexpected error during chatbot loop.")
        raise ChatbotExceptionError(
            "Something went wrong with chatbot. please check logs."
        )


# -------------------- Main App -------------------- #

def main() -> None:
    try:
        logger.info("Application started.")

        agent = get_agent()

        print("""
             \tWelcome to the ABCD Bank chatbot v0.0.1
             \tI can help you with all your questions!\n
             """)

        user_name = input("Bot : Please enter your name: ").strip()
        logger.info(f"User entered name: {user_name}")

        greetings = get_greetings(user_name, agent)
        print(greetings)

        startup_chatbot(agent)
        loop_chatbot(agent)

    except ChatbotExceptionError as e:
        logger.exception("ChatbotExceptionError occurred in main.")
        print("Bot : {}".format(e))

    except Exception as e:
        logger.exception("Unhandled exception occurred in main.")
        print("Exception : {}".format(e))

    finally:
        logger.info("Application execution completed.")
        print("+" * 80)
        print("execution completed")
        print("+" * 80)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger("chatbot")

    logger.info("Initializing chatbot application.")

    base_llm_message = [SystemMessage(content=system_prompt)]
    loop_chat_llm_message = [SystemMessage(content=system_prompt)]

    main()