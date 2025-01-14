#!/usr/bin/env python3

from plumbum import local
import os

def debug(message: str):
    print(f'##[debug]{message}')


def run():
    netrc_path = os.path.join(local.env.get('HOME', ''), '.netrc')
    github_actor = local.env.get('INPUT_ACTOR') or local.env.get('GITHUB_ACTOR')
    github_token = local.env.get('INPUT_GITHUB-TOKEN')
    commit_message = local.env.get('INPUT_COMMIT-MESSAGE')
    force_add = local.env.get('INPUT_FORCE-ADD')
    force_push = local.env.get('INPUT_FORCE-PUSH')
    branch = local.env.get('INPUT_PUSH-BRANCH') or local.env.get('GITHUB_REF').split('/')[2]
    rebase = local.env.get('INPUT_REBASE', 'false')
    files = local.env.get('INPUT_FILES', '')
    email = local.env.get('INPUT_EMAIL', f'{github_actor}@users.noreply.github.com')
    name = local.env.get('INPUT_NAME', github_actor)
    with open(netrc_path, 'w') as f:
        f.write(
            f'machine github.com\n'
            f'login {github_actor}\n'
            f'password {github_token}\n'
            f'machine api.github.com\n'
            f'login {github_actor}\n'
            f'password {github_token}\n',
        )
    chmod = local['chmod']
    git = local['git']
    debug(chmod(['600', netrc_path]))
    debug(git(['config', '--global', 'user.email', email]))
    debug(git(['config', '--global', 'user.name', name]))
    debug(f'username:{github_actor}, branch:{branch}, commit message:{commit_message}')
    with open(netrc_path) as f:
        debug(f.read())
    add_args = ['add']
    if force_add == 'true':
        add_args.append('-f')
    add_args.append('-A')
    if files:
        add_args.append(files)
    if rebase == 'true':
        debug(git(['pull', '--rebase', '--autostash', 'origin', branch]))
    debug(git(['config', '--global', '--add', 'safe.directory', '/github/workspace']))
    debug(git(['checkout', '-B', branch]))
    debug(git(add_args))
    debug(git(['commit', '-m', commit_message], retcode=None))
    push_args = ['push']
    if force_push == 'true':
        push_args.append('--force')
    push_args.append('--follow-tags')
    push_args.append('--set-upstream')
    push_args.append('origin')
    push_args.append(branch)
    debug(git(push_args))

if __name__ == '__main__':
    run()
