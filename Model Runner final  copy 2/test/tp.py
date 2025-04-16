# text_processor.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="Processes a text string.")
    parser.add_argument("--input_text", type=str, required=True, help="The text to process")
    args = parser.parse_args()

    text = args.input_text
    uppercase_text = text.upper()
    word_count = len(text.split())

    output_text = f"Original Text: {text}\nUppercase Text: {uppercase_text}\nWord Count: {word_count}"
    print(output_text)

if __name__ == "__main__":
    main()