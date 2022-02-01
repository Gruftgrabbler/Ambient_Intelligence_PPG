#!/usr/bin/env python
import os
from os.path import exists

import yaml

GH_JOBS_YML = ".github/workflows/static_code_analysis.yml"
LS = os.linesep


def run_shell_command(command_str: str):
    commands = command_str.split("\n")

    for command in commands:
        if command == "":
            continue
        print(command)
        output = os.popen(command)

        while True:
            line = output.readline()

            if line:
                print(line, end="")
            else:
                break

    output.close()


print("Trying to find the GitHub Workflows directory and jobs.yml...")
if not exists(GH_JOBS_YML):
    print("Could not find the GitHub Workflows Actions *.yml file. "
          "Are you executing the file from the correct project root directory?")
    print(f"==> Current Working Directory: {os.getcwd()}")

print("GitHub Workflows Actions *.yml file found. Analyzing it's content now...")

with open(GH_JOBS_YML) as f:
    gh_actions_yml_dict = yaml.load(f, Loader=yaml.SafeLoader)
    jobs_remaining = list(gh_actions_yml_dict["jobs"].keys())
    jobs_already_run = []

    print(
        f"Found the following jobs to run:{LS}{jobs_remaining}{LS * 2} => Starting now...{LS * 2}"
    )

    for job in gh_actions_yml_dict["jobs"]:
        current_job_definition = gh_actions_yml_dict["jobs"][job]

        print(f"Checking the '{job}' stage...")
        job_commands = ""
        for job_step in current_job_definition["steps"]:

            try:
                job_cmd = job_step["run"]
                job_commands += job_cmd
            except KeyError:
                pass

        if not job_commands:
            print(f"The '{job}' contains no commands.")
            continue

        print(f"The '{job}' contains commands.")
        try:
            print(
                f"The '{job}' job needs these jobs '[{current_job_definition['needs']}]' to be run prior to its "
                f"execution. Delaying it..."
            )
        except KeyError:
            print(
                f"The '{job}' stage does not depend on other jobs and can be run immediately."
            )
            print(f"Running the '{job}' stage:")
            run_shell_command(job_commands)
            jobs_remaining.remove(job)
            jobs_already_run.append(job)

    while jobs_remaining:
        for job in jobs_remaining:
            current_job_definition = gh_actions_yml_dict["jobs"][job]

            print(f"Checking the '{job}' stage...")
            job_commands = ""
            for job_step in current_job_definition["steps"]:

                try:
                    job_cmd = job_step["run"]
                    job_commands += job_cmd
                except KeyError:
                    pass

            if not job_commands:
                print(f"The '{job}' contains no commands.")
                continue

            print(f"The '{job}' contains commands.")

            if current_job_definition["needs"] == jobs_already_run:
                print(
                    f"The '{job}' jobs dependencies '[{current_job_definition['needs']}]' have already run."
                )
                print(f"Running the '{job}' stage now:")
                run_shell_command(job_commands)
                jobs_remaining.remove(job)
                jobs_already_run.append(job)

    print("All GitHub Action Jobs have run! :-)")
