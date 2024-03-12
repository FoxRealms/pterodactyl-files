#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from typing import Iterator, NamedTuple

class Context(NamedTuple):
	system: str
	java: str
	tag: str


def iterate_all() -> Iterator[Context]:
	for system in ['debian', 'centos']:
		for java in [7, 8, 11, 17, 21]:
			tag = f'bluefunny/pterodactyl:general-java-{system}-{java}'
			yield Context(system, str(java), tag)


def cmd_build(args: argparse.Namespace):
	for ctx in iterate_all():

		print(f'======== System: {ctx.system}, Java: {ctx.java}, Tag: {ctx.tag!r} ========')

		cmd = [
			'docker', 'build', os.getcwd(),
			'-t', ctx.tag,
			'--build-arg', f'SYSTEM={ctx.system}',
			'--build-arg', f'JAVA_VERSION={ctx.java}',
			'-f', f'./files/Dockerfile.{ctx.system}',
		]
		if args.http_proxy is not None:
			cmd.extend([
				'--build-arg', f'http_proxy={args.http_proxy}',
				'--build-arg', f'https_proxy={args.http_proxy}',
			])
		subprocess.check_call(cmd)

		if args.push:
			subprocess.check_call(['docker', 'push', ctx.tag])


def cmd_push(args: argparse.Namespace):
	for ctx in iterate_all():
		subprocess.check_call(['docker', 'push', ctx.tag])


def cmd_delete(args: argparse.Namespace):
	for ctx in iterate_all():
		subprocess.check_call(['docker', 'image', 'rm', ctx.tag])


def main():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(title='Command', help='Available commands', dest='command', required=True)

	parser_build = subparsers.add_parser('build', help='Build all images')
	parser_build.add_argument('-p', '--push', action='store_true', help='Push after build')
	parser_build.add_argument('--http-proxy', help='Set the url of http proxy to be used in build')

	subparsers.add_parser('push', help='Push all images')
	subparsers.add_parser('delete', help='Delete all images')

	args = parser.parse_args()

	if args.command == 'build':
		cmd_build(args)
	elif args.command == 'push':
		cmd_push(args)
	elif args.command == 'delete':
		cmd_delete(args)
	else:
		print('Unknown command {!r}'.format(args.command))
		sys.exit(1)


if __name__ == '__main__':
	try:
		main()
	except subprocess.CalledProcessError as e:
		print(type(e).__name__, e.returncode, file=sys.stderr)
	except KeyboardInterrupt:
		pass
