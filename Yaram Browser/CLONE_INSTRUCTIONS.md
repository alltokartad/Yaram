Clone instructions for Yaram Browser

- To create a test clone of the project, run the `create_clone.bat` script in the project root. This will create a folder named `Yaram_Browser_Clone` containing a copy of the project.

- To create a clone and immediately run the cloned browser, run `create_clone_and_run.bat`.

PowerShell example:

```powershell
cd "c:\Users\Melinda\source\repos\Yaram Browser"
./create_clone.bat
# or to copy and run immediately
./create_clone_and_run.bat
```

Notes:
- The clone will include all files in the project folder. If you want to exclude dev artifacts, delete them from the clone folder after creation.
- The cloned copy runs with the same Python interpreter as your system `py` launcher.
- If packages are missing in the environment, install them before running (for example `py -m pip install PyQt5 PyQtWebEngine`).
