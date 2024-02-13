


# Basics of Logging - ELI5
Imagine you're playing with a giant, intricate LEGO set that sometimes doesn't fit together the way it's supposed to. Logging is like keeping a diary of every step you take while playing. If something goes wrong, you can look back at your diary and see exactly where the pieces didn't fit.

### Core Concepts of Logging:

1. **What's a Log?**
   - A log is like a note or diary entry that your software writes every time it does something important, like when it successfully completes a task or when it runs into trouble.

2. **Why Log?**
   - Just like how you might say "Yay!" when you fit a tricky LEGO piece in place or "Uh-oh" when it doesn't fit, logs help us know when things are going well in our software and alert us when they're not.

3. **Levels of Logging:**
   - Imagine if for every LEGO piece you add, you can say "This is easy" (INFO), "Hmm, this is a bit tricky" (WARNING), or "Help! I can't do this!" (ERROR). In logging, we have similar levels to express how serious a situation is.

### Best Practices Simplified:

1. **Keep it Clear and Useful:**
   - Your diary entries should be easy to understand. Instead of writing "I did something," write "I built the spaceship's cockpit."

2. **Don't Write Too Much or Too Little:**
   - If you write about every tiny piece you touch, your diary will be too full, and finding important information will be like finding a needle in a haystack. But if you write too little, you might miss the details you need to fix a problem.

3. **Protect Your Secrets:**
   - If your diary has a secret code to a treasure chest, don't leave it where others can read it! Similarly, make sure your logs don't contain private information like passwords.

4. **Use the Right Tools:**
   - Just like you might have a special box for your favorite LEGO pieces, there are tools designed to keep and look at logs. These tools can help you find exactly what went wrong and when.

5. **Check Your Logs Regularly:**
   - It's like looking back at your LEGO diary every so often to see what you've built and if you've made any mistakes you didn't notice at the time.

By following these practices, logging becomes a powerful tool to help keep your software "LEGO land" running smoothly and makes it easier to fix any issues that pop up along the way.













# What to include in a Log
Including relevant data in your logs is crucial for diagnosing issues, understanding the state of your application, and making informed decisions based on the logged information. Here's what you might consider including in logs of different levels, along with the importance of metadata like version numbers and dyno identifiers:

### General Information for All Log Levels

- **Timestamp**: The exact time an event occurred. It's essential for tracking when something happened in the application flow.
- **Log Level**: The severity of the log entry (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). Helps in filtering logs based on importance.
- **Message**: A clear, descriptive message explaining what happened. This should be understandable without needing to dive into the code.
- **Request ID**: If applicable, include a unique identifier for the request or transaction. This helps in tracing logs related to a specific user action or request.

### Additional Data for Higher Log Levels (ERROR, CRITICAL)

- **Error Details**: Include exception messages, stack traces, or error codes to provide context about the error.
- **Affected User or Session Info**: Knowing which user encountered the error can help in reproducing and diagnosing issues.
- **Affected System or Component**: Indicate which part of the application or system is involved, especially in microservices or distributed architectures.

### The Importance of Metadata

- **Version Number**: Including the application version or release number in logs is crucial for identifying issues related to specific releases. It helps in understanding whether a bug is tied to a recent code change or deployment.
- **Environment Info**: Indicating the environment (development, staging, production) can prevent confusion, especially if logs from different environments are aggregated together.
- **Dyno or Instance Identifier**: In platforms like Heroku, including the dyno ID or instance number helps in identifying issues that might be isolated to a specific instance or dyno. This is particularly useful for troubleshooting problems that don't affect the entire application.
- **Hostname or IP Address**: Knowing the source of the log can be useful in distributed systems to identify which server or container generated the log.

### Best Practices

- **Structured Logging**: Use a structured format like JSON for logs. This makes it easier to parse and query logs, especially when including various data points.
- **Consistency**: Maintain consistent logging practices across your application. This includes consistent formatting, terminology, and data inclusion.
- **Security**: Be cautious about logging sensitive information. Avoid logging personal identifiable information (PII), passwords, API keys, etc., to comply with security and privacy standards.
- **Configuration**: Allow flexibility in your logging configuration to adjust the verbosity and data inclusion based on the environment. For example, you might include more verbose logs in development compared to production.

Incorporating these pieces of information and practices in your logging strategy enhances the observability and debuggability of your application, making it easier to monitor its health, diagnose issues, and understand its behavior in different situations.
















# Examples of good logging using Heroku + Python
Good logging practices help you monitor your application's health, diagnose issues, and understand its behavior. When using Heroku and Python, you can leverage Heroku's log management capabilities and Python's built-in `logging` module to implement effective logging. Here's how you can do it with some best practices:

### 1. Use Python's Built-in Logging Module

Python's `logging` module is powerful and flexible. It's preferable over using `print` statements because it allows you to set different log levels and easily control the output format.

#### Example Setup:

```python
import logging
import sys

# Configure basic settings for logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Example usage
logger.info('Starting the application')
try:
    # Your application logic here
    logger.info('Application is running')
except Exception as e:
    logger.error('An error occurred: %s', str(e))
```

In this setup:
- Logs are directed to `sys.stdout` so Heroku can capture them.
- The log level is set to `INFO`, meaning all INFO, WARNING, ERROR, and CRITICAL messages will be logged.
- A format is specified for log messages, including a timestamp, the logger's name, the log level, and the message.

### 2. Use Different Log Levels Appropriately

Utilize various log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) to indicate the severity of log messages. This helps in filtering logs for relevant information.

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems.
- **INFO**: Confirmation that things are working as expected.
- **WARNING**: An indication that something unexpected happened, or indicative of some problem in the near future (e.g., 'disk space low'). The software is still working as expected.
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function.
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running.

### 3. Structured Logging

Consider using structured logging, especially for complex applications. Structured logs are easier to analyze and query, especially when using log management tools.

#### Example of Structured Logging:

```python
import json

def log_structured(level, message, **kwargs):
    log_entry = {
        'level': level,
        'message': message,
        'extra': kwargs
    }
    print(json.dumps(log_entry))

log_structured('INFO', 'User logged in', user_id='12345')
```

### 4. Handle Exceptions Properly

Make sure to log exceptions with sufficient detail. Use `logger.exception()` within an `except` block to automatically include stack trace information in the log.

```python
try:
    # risky operation
except Exception as e:
    logger.exception('Unexpected error occurred')
```

### 5. Periodic Log Review and Rotation

While Heroku captures and aggregates logs, for long-term storage and analysis, consider using add-ons like Papertrail or Logentries. These services offer features like log rotation, search capabilities, and alerting.

### 6. Environment-specific Configuration

Adjust logging verbosity based on the environment. For instance, use a higher log level (like `DEBUG`) in development and a lower one (`INFO` or `WARNING`) in production to reduce log volume.

### 7. Avoid Logging Sensitive Information

Be cautious not to log sensitive information such as passwords, API keys, or personal identifiable information (PII) to comply with security and privacy standards.

### Conclusion

Following these best practices in logging with Heroku and Python will help you maintain a healthy, observable, and maintainable application. Proper logging practices are essential for effective application monitoring, troubleshooting, and security.















# What is Stdin Stdout
In the context of logging, especially in environments like Heroku, `stdin`, `stdout`, and `stderr` refer to standard streams used by a computer program to interact with its environment, typically a terminal or another program.

### `stdin` (Standard Input)
- **What it is**: `stdin` is the standard input stream, which provides input to programs. It's often connected to the keyboard or another input source by default.
- **In Logging Context**: While `stdin` is crucial for interactive programs that require user input, it's less relevant in the context of logging, as logs are outputs generated by the program.

### `stdout` (Standard Output)
- **What it is**: `stdout` is the standard output stream where a program writes its output data. By default, this output is displayed in the terminal.
- **In Logging Context**: In Heroku and similar platforms, logs written to `stdout` are captured by the platform's logging system. Therefore, for logging purposes, you should configure your application to write logs to `stdout`. This ensures that your logs are captured and can be viewed through Heroku's log viewing tools (`heroku logs` command, Heroku Dashboard, etc.).

### `stderr` (Standard Error)
- **What it is**: `stderr` is the standard error stream, which is used specifically for outputting error messages and diagnostics from a program. Like `stdout`, `stderr` typically displays in the terminal, but it's treated separately so that errors can be redirected or handled differently from standard output.
- **In Logging Context**: Writing error logs to `stderr` is a common practice. This separation allows for more granular control over how errors are logged and handled. Heroku also captures `stderr` output, making it available alongside `stdout` in the aggregated logs.

### Summary
In the context of Heroku and application logging:
- Write your regular log messages (e.g., informational, debug messages) to `stdout`.
- Write error messages or warnings to `stderr`.
- This practice ensures that all log output is captured by Heroku's logging infrastructure, making it accessible for monitoring, debugging, and analysis.