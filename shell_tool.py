"""
title: Shell Command Executor
author: infra
version: 1.0
"""

import subprocess
import json


class Tools:
    class Valves:
        pass

    def __init__(self):
        pass

    async def run_command(self, command: str) -> str:
        """
        Execute a shell command on the host system and return the output.
        Use for system operations like checking RAM, disk space, processes, files, etc.

        :param command: The shell command to execute on the host
        :return: The command's stdout and stderr output
        """
        try:
            result = subprocess.run(
                ["nsenter", "-t", "1", "-m", "-u", "-i", "-n", "-p", "--", "sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = (result.stdout + result.stderr).strip()
            if not output:
                return "(no output)"
            if len(output) > 8000:
                output = output[:8000] + "\n... (truncated)"
            return output
        except subprocess.TimeoutExpired:
            return "Error: command timed out after 30 seconds"
        except Exception as e:
            return f"Error: {str(e)}"

    async def get_system_info(self) -> str:
        """
        Get comprehensive system information: hostname, OS, RAM, disk, CPU, uptime, load average. Returns JSON.

        :return: JSON string with system information
        """
        try:
            info = {}

            def run(cmd):
                r = subprocess.run(
                    ["nsenter", "-t", "1", "-m", "-u", "-i", "-n", "-p", "--", "sh", "-c", cmd],
                    capture_output=True, text=True, timeout=10,
                )
                return r.stdout.strip()

            info["hostname"] = run("hostname")
            info["os"] = run("uname -a")
            info["ram"] = run("free -h")
            info["disk"] = run("df -h /")
            info["uptime"] = run("uptime")
            info["cpu_cores"] = run("nproc")
            info["load"] = run("cat /proc/loadavg")
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

    async def list_directory(self, path: str = "/home/radxa") -> str:
        """
        List the contents of a directory on the host system.

        :param path: The directory path to list (default: /home/radxa)
        :return: Directory listing
        """
        try:
            result = subprocess.run(
                ["nsenter", "-t", "1", "-m", "-u", "-i", "-n", "-p", "--", "ls", "-lah", path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = (result.stdout + result.stderr).strip()
            if len(output) > 8000:
                output = output[:8000] + "\n... (truncated)"
            return output if output else "(no output)"
        except Exception as e:
            return f"Error: {str(e)}"
