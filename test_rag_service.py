from dotenv import load_dotenv

load_dotenv()

from rag.rag_service import RagService


def main():
    rag_service = RagService()

    question = "What is DNS?"

    result = rag_service.ask(question)

    print("\nQuestion:")
    print(result["question"])

    print("\nRetrieved context:")
    for i, chunk in enumerate(result["context"], start=1):
        print(f"{i}. {chunk}")

    print("\nAnswer:")
    print(result["answer"])


if __name__ == "__main__":
    main()