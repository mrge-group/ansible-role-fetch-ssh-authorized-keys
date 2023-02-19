#!/usr/bin/env python3

"""A script to lookup authorized_keys with Ansible

This should be a lookup-plugin but sadly those can not use become and
only root has access to all known_hosts files.
"""

# included
from pathlib import Path

# 3rd-party
from ansible.module_utils.basic import AnsibleModule


def get_passwd():
    """Reads all entries from /etc/shadow"""
    with open('/etc/passwd', encoding='utf-8') as file_handler:
        for line in file_handler.readlines():
            yield line.split(':')


def filter_passwd(users):
    """Matches for valid users with existing home-dirs"""
    for user in users:
        if len(user) != 7:
            continue
        name = user[0]
        home = Path(user[5])
        if not home.is_dir():
            continue
        yield (name, home)


def read_keys(home):
    """Read the authorized_keys with a given home-dir"""
    keys_path = home.joinpath('.ssh', 'authorized_keys')
    if not keys_path.exists():
        keys_path = home.joinpath('.ssh', 'authorized_keys2')
    if keys_path.exists():
        with keys_path.open() as file_handler:
            for line in file_handler.readlines():
                yield line.rstrip()


def main():
    """Execute as Ansible-Module"""
    result = {}
    result['changed'] = False

    module = AnsibleModule(argument_spec={}, supports_check_mode=True)

    users = get_passwd()
    users = filter_passwd(users)
    fetched_keys = {}
    for (user, home) in users:
        keys = sorted(read_keys(home))
        if keys:
            fetched_keys[user] = keys

    result['authorized_keys'] = fetched_keys
    module.exit_json(**result)


if __name__ == '__main__':
    main()

# [EOF]
