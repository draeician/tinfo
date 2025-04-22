# Text Information Analyzer

The Text Information Analyzer is a Python command-line tool that provides statistics on a text file, including token count, character count, word count, and line count. It uses the Tiktoken library for accurate token counting.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-username/text-information-analyzer.git



Navigate to the project directory:
cd text-information-analyzer



Install the required dependencies:
pip install tiktoken



Usage
To use the Text Information Analyzer, follow these steps:


Navigate to the project directory:
cd text-information-analyzer



Run the script with the path to your text file as an argument:
./tinfo.py /path/to/your_text_file.txt

Replace /path/to/your_text_file.txt with the actual path to your text file.


The script will analyze the file and provide the following information:

Token count: The number of tokens in the file.
Character count: The total number of characters in the file.
Word count: The total number of words in the file.
Line count: The total number of lines in the file.

Example
./tinfo.py sample.txt

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments

The Tiktoken library: https://github.com/awslabs/tiktoken

