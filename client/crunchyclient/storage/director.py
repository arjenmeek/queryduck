import argparse

from .filesystem import VolumeHandler

class StorageDirector(object):

    def __init__(self, master):
        self.master = master
        self.api = self.master.api

        parser_single_volume = argparse.ArgumentParser(add_help=False)
        parser_single_volume.add_argument('-r', '--reference', required=True)

        parser_update_volume = argparse.ArgumentParser(add_help=False)
        parser_update_volume.add_argument('-r', '--reference', required=True)
        parser_update_volume.add_argument('-p', '--path', required=True)

        parser_dumb = argparse.ArgumentParser(add_help=False)

        self.master.register_command_parser('list_volumes', parser_dumb, self.action_list_volumes)
        self.master.register_command_parser('new_volume', parser_single_volume, self.action_new_volume)
        self.master.register_command_parser('delete_volume', parser_single_volume, self.action_delete_volume)
        self.master.register_command_parser('update_volume', parser_update_volume, self.action_update_volume)

    def action_list_volumes(self, args):
        """List all Volumes"""
        volumes = self.api.find_raw_volumes()
        for volume in volumes:
            print(volume['id'], volume['reference'])

    def action_new_volume(self, args):
        """Create a new Volume"""
        volume = {"reference": args.reference}
        self.api.save_raw_volume(volume)

    def action_delete_volume(self, args):
        """Delete a Volume"""
        reference = args.reference
        self.api.delete_volume(args.reference)

    def action_update_volume(self, args):
        """Update a Volume's files"""
        volume = self.api.get_raw_volume(args.reference)
        vh = VolumeHandler(volume, self.api)
        vh.update(args.path)
