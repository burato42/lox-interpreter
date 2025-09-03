import sys

from app.scanner import Scanner


def main():
    print("Logs from your program will appear here!", file=sys.stderr)

    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()


    exit_code = 0
    scanner = Scanner(file_contents)
    tokens, errors = scanner.scan_tokens()

    if errors:
        exit_code = 65
        for error in errors:
            print(error, file=sys.stderr)

    for token in tokens:
        print(token)

    if exit_code != 0:
        exit(exit_code)


if __name__ == "__main__":
    main()
