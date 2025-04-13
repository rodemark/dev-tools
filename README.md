# dev-tools – a set of utilities for developers.

## Logger

Logger is a module for handling application logging. It provides:

- **Multiple Log Levels:** Use levels like DEBUG, INFO, WARNING, ERROR, and CRITICAL to filter log output.
- **Colored Console Output:** Displays log messages in different colors based on their level.
- **Automatic Log Rotation:** Automatically rotates log files daily and compresses older logs.

### Usage Example

```python
from dev_tools.logging_tools.logger import MyLogger

logger = MyLogger()
logger.info("Application started.")
```

---

## Git Tools

Git Tools is a module for analyzing your repository's commit history. It provides:

- **Commit Summary:** Displays total commit counts within a specified period and groups them by author.
- **ASCII Commit Graph:** Prints a visual commit graph directly in the terminal.
- **Filtering Options:** Filter results by date (dd-mm-yyyy), author, and branch (with branch existence verification).

### Usage Examples

- **Commit Summary:**

  ```bash
  python3 dev_tools/git_tools/git_tool.py --start-date 01-04-2025 --end-date 30-04-2025
  ```

- **Filter by Author:**

  ```bash
  python3 dev_tools/git_tools/git_tool.py -sd 01-04-2025 -ed 30-04-2025 -a "John Doe"
  ```

- **Filter by Branch:**

  ```bash
  python3 dev_tools/git_tools/git_tool.py -sd 01-04-2025 -ed 30-04-2025 -b develop
  ```

---