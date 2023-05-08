<div align="center">
  <div>
    <h1 align="center">AI Dev</h1>
  </div>
  <p>
    <strong>
    Are you tired of making small code changes only to have a series of CI tests fail afterward? <br> 
    Introducing an AI-powered(Chatgpt/gpt4) solution to <br> 
    </strong>
  </p>

  <p>✨ Run mock tests before committing</p>
  <p>🚀 Get valuable suggestions to improve your code before you commit</p>
  <p>🛠 Automatically generate unit tests for your code changes before committing</p>
  <p>📝 Generate insightful commit messages automatically based on your code changes</p>

  <a href="https://pypi.org/project/aidev/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/aidev">
    </a>
    <a href="https://github.com/voidful/aidev">
        <img alt="Download" src="https://img.shields.io/pypi/dm/aidev">
    </a>
    <a href="https://github.com/voidful/aidev">
        <img alt="Last Commit" src="https://img.shields.io/github/last-commit/voidful/aidev">
    </a>
</div>

---

## 🌟 Features

- Run mock tests on your latest code changes before committing, powered by AI
- Get actionable code improvement suggestions to optimize your codebase
- Automatically generate unit tests for your code changes, saving you time and effort
- Easy-to-use CLI with configuration options for a tailored experience
- Improve code quality, reduce technical debt, and increase confidence in your commits

## 📦 Installation

Install the AI Test package using pip:

```bash
pip install aidev
```

## 🚀 Quick Start

After installation, use the aidev command to analyze your code changes:

```bash
aidev
```

You can customize the behavior of the CLI using various options:

```bash
aidev --threshold 0.8 --engine gpt-3.5-turbo --max-tokens 400
```

For more information on available options, run:

```bash
aidev --help
```

### ⚙️ Configuration

AI Tester allows you to configure various settings to better suit your needs. To manage and edit these configurations,
use the `aidev-config` CLI command.

#### Configurable settings include:

- **API Key**: Store your OpenAI API key in a local configuration file. The CLI tool will guide you through entering and
  storing the key the first time you use it.
- **Threshold**: Set the confidence threshold for the AI-generated results (ranging from 0.0 to 1.0).
- **Engine**: Choose the GPT engine to use (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-32k").
- **Max Tokens**: Specify the maximum number of tokens in the AI-generated response.
- **Language**: Set the output language for the AI-generated response.

#### Configuration management:

The `aidev-config` CLI command allows you to view, add, update, or remove configuration settings. The command provides a
user-friendly interface to manage your settings.

To set up and manage the configuration, follow these steps:

1. Run the `aidev-config` command with the desired subcommand, e.g., `aidev-config set-api-key <your-api-key>`.
2. The CLI will update the configuration with the provided value.
3. Use `aidev-config show-config` to view the current configuration settings.

The main CLI tool, `aidev`, reads the configuration settings and applies them when generating AI responses, ensuring a
customized experience based on your preferences.

### 📚 How it works

AI Test harnesses the power of OpenAI's GPT-4 to provide real-time assistance for developers. When you run the CLI tool
with your code changes, it performs the following steps:

- Retrieve code changes: The tool first runs git diff to capture the latest code changes in your repository.
- Generate a prompt: Depending on your chosen action (mock test, code suggestions, or unit test generation), the CLI
  tool creates a prompt for the AI model to understand the task.
- Interact with GPT-4: The tool sends the prompt to GPT-4, which processes the information and generates a relevant
  response.
- Display the results: The AI-generated results are displayed in the CLI, providing you with mock test outcomes, code
  improvement suggestions, or unit test examples based on your request.

By leveraging AI technology, AI Test streamlines your development process, making it more efficient, accurate, and
enjoyable.

### 🌱 Contribute

We welcome contributions! Feel free to open issues, submit pull requests, or start discussions on improving AI Test.

### 📃 License

This project is licensed under the MIT License.

#### 🚀 Empower your code commit workflow with AI Test today! Give it a try, and don't forget to ⭐️ the repository if you find it helpful!

