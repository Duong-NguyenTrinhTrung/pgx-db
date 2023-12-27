### Run many build data scripts

Use nohup to run the build data scripts in the background.
  
```bash
chmod +x run_build_data_scripts.sh
nohup ./run_build_data_scripts.sh &
```

Then check the log file to see if the scripts are running.

```bash
tail -f nohup.out
```