# Ansible provisioning

Reproducible setup for a machine that builds/runs the Botwheel explorer.

## Requirements

```bash
sudo apt install ansible
```

## Usage

Run everything against the local machine (you'll be prompted for the sudo password):

```bash
cd ansible
ansible-playbook playbooks/main.yml --ask-become-pass
```

Run a single playbook:

```bash
cd ansible
ansible-playbook playbooks/task.yml --ask-become-pass
```

To provision a remote host (e.g. the robot's onboard computer), uncomment and
edit the `[robots]` entry in `inventory/hosts`, then limit the run to it:

```bash
ansible-playbook playbooks/main.yml --ask-become-pass --limit robots
```

## Playbooks

- `task.yml` — installs [Taskfile (go-task)](https://taskfile.dev) from the
  official Cloudsmith apt repository.
- `main.yml` — imports every playbook above; the entry point for a full provision.
