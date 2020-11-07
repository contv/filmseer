# setup.py
# This is a set up script that is used to test connection and libraries,
# create database tables and so on.
import sys

import tortoise
from dotenv import dotenv_values, find_dotenv

from app.core.config import settings


async def init_database(drop_all: bool = False, if_not_exists: bool = True):
    env_dict = dotenv_values(find_dotenv(filename=".env"))
    if (env_dict.get("SSH_TUNNEL_ENABLED", "True").lower().strip()) in [
        "y",
        "yes",
        "1",
        "true",
    ]:
        print()
        print()
        print(" ========================WARNING========================= ")
        print(" =====================W A R N I N G====================== ")
        print(" ==================[[ W A R N I N G ]]=================== ")
        print(" ||                                                    || ")
        print(" ||               SSH Tunnel is ENABLED                || ")
        print(" ||      You WILL RE-SETUP the REMOTE database!!       || ")
        print(" ||                                                    || ")
        print(" || Type 'YES, I DO KNOW WHAT I AM DOING' to continue. || ")
        print(" ||        Your reply must be EXACTLY the same.        || ")
        print(" ||                                                    || ")
        print(" ======================================================== ")
        confirmation = input()
        if confirmation.strip() != "YES, I DO KNOW WHAT I AM DOING":
            print("Exited.")
            sys.exit(1)
        else:
            print()
            print("I surely hope what you are doing.")
            print()
            print("Connecting SSH Tunnel...")
            print()

        import json
        import re
        from urllib.parse import urlparse

        from sshtunnel import SSHTunnelForwarder

        ssh_server_list = []
        try:
            json_object = json.loads(env_dict.get("SSH_TUNNEL_LIST_JSON", ""))
        except ValueError:
            print("ERROR: SSH_TUNNEL_LIST_JSON value is not a valid JSON")
            sys.exit(1)

        for ssh_object in json_object:
            bastion_url = ssh_object["bastion_url"]
            ssh_key = ssh_object["ssh_key"]
            remote_bind = ssh_object["remote_bind"]
            local_bind = ssh_object["local_bind"]
            try:
                bastion_parsed = urlparse(bastion_url)
            except ValueError:
                print(
                    "ERROR: Bastion value "
                    + bastion_url
                    + " is not a valid value. Valid value is "
                    + "ssh://user(:password)@host:port"
                )
                sys.exit(1)

            bastion_user = bastion_parsed.username
            bastion_host = bastion_parsed.hostname
            bastion_port = bastion_parsed.port
            bastion_password = bastion_parsed.password
            try:
                remote_regex = re.search(r"(.*):(.*)", remote_bind)
            except ValueError:
                print(
                    "ERROR: Remote value "
                    + remote_bind
                    + " is not a valid value. Valid value is host:port"
                )
                sys.exit(1)

            remote_host = remote_regex.group(1)
            remote_port = int(remote_regex.group(2))

            try:
                local_regex = re.search(r"(.*):(.*)", local_bind)
            except ValueError:
                print(
                    "ERROR: Local value "
                    + local_bind
                    + " is not a valid value. Valid value is host:port"
                )
                sys.exit(1)

            local_host = local_regex.group(1)
            local_port = int(local_regex.group(2))

            server_ssh = SSHTunnelForwarder(
                (bastion_host, bastion_port),
                ssh_username=bastion_user,
                ssh_password=bastion_password,
                ssh_pkey=ssh_key,
                remote_bind_address=(remote_host, remote_port),
                local_bind_address=(local_host, local_port),
            )

            ssh_server_list.append(server_ssh)

        for ssh_tunnel in ssh_server_list:
            ssh_tunnel.start()
    else:
        print("Setting up the local database...")

    await tortoise.Tortoise.init(
        db_url=settings.DATABASE_URI, modules={"models": ["app.models.db"]}
    )
    conn = tortoise.Tortoise.get_connection("default")
    if drop_all:
        command_items = await conn.execute_query_dict(
            "SELECT 'DROP TABLE IF EXISTS "
            "\"' || tablename || '\""
            " CASCADE;' AS cmd FROM pg_tables WHERE schemaname = current_schema();"
        )
        for command_item in command_items:
            await conn.execute_query(command_item["cmd"])
    await tortoise.Tortoise.generate_schemas(safe=if_not_exists)
    await add_constraints(conn)
    await tortoise.Tortoise.close_connections()
    print("Finished.")


def setup_clean():
    tortoise.run_async(init_database(drop_all=True, if_not_exists=True))


def setup_noclean():
    tortoise.run_async(init_database(drop_all=False, if_not_exists=True))


def setup_nodrop():
    tortoise.run_async(init_database(drop_all=False, if_not_exists=False))


async def add_constraints(conn):
    await conn.execute_query("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    await conn.execute_query(
        """
        ALTER TABLE public.movie_genres
        ALTER COLUMN moviegenre_id
        SET DEFAULT gen_random_uuid()
        """
    )
    await conn.execute_query(
        """
        ALTER TABLE public.positions
        ALTER COLUMN position_id
        SET DEFAULT gen_random_uuid()
        """
    )
    await conn.execute_query(
        """
        ALTER TABLE public.ratings
        ALTER COLUMN rating_id
        SET DEFAULT gen_random_uuid()
        """
    )
