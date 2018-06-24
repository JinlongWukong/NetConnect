import time
import re

from netconnect.extends.base_connection import BaseConnection

class NsoConnection(BaseConnection):
    """Base Class for nso behavior."""

    def session_preparation(self):
        """Prepare the session after the connection has been established."""
        self._test_channel_read()
        self.set_base_prompt()
        self.disable_paging(command="set paginate false")
        # Clear the read buffer
        time.sleep(.3 * self.global_delay_factor)
        self.clear_buffer()

    def send_config_set(self, config_commands=None, exit_config_mode=False, **kwargs):
        """nso requires you not exit from configuration mode."""
        return super().send_config_set(config_commands=config_commands,
                                                       exit_config_mode=False, pattern=True, **kwargs)

    def commit(self, confirm=False, confirm_delay=None, comment='', label='', delay_factor=1, options=''):
        """
        Commit the candidate configuration.

        default (no options):
            command_string = commit
        confirm and confirm_delay:
            command_string = commit confirmed <confirm_delay>
        label (which is a label name):
            command_string = commit label <label>
        comment:
            command_string = commit comment <comment>
        options:
            command_string = commit options <no-networking, dry-run ...>
        supported combinations
        label and confirm:
            command_string = commit label <label> confirmed <confirm_delay>
        label and comment:
            command_string = commit label <label> comment <comment>

        All other combinations will result in an exception.

        failed commit message:
        % Failed to commit one or more configuration items during a pseudo-atomic operation. All
        changes made have been reverted. Please issue 'show configuration failed [inheritance]'
        from this session to view the errors

        message nso shows if other commits occurred:
        One or more commits have occurred from other configuration sessions since this session
        started or since the last commit was made from this session. You can use the 'show
        configuration commit changes' command to browse the changes.

        Exit of configuration mode with pending changes will cause the changes to be discarded and
        an exception to be generated.
        """
        delay_factor = self.select_delay_factor(delay_factor)
        if confirm and not confirm_delay:
            raise ValueError("Invalid arguments supplied to nso commit")
        if confirm_delay and not confirm:
            raise ValueError("Invalid arguments supplied to nso commit")
        if comment and confirm:
            raise ValueError("Invalid arguments supplied to nso commit")

        # wrap the comment in quotes
        if comment:
            if '"' in comment:
                raise ValueError("Invalid comment contains double quote")
            comment = '"{0}"'.format(comment)

        label = str(label)
        error_marker = 'Error'
        alt_error_marker = 'One or more commits have occurred from other'

        # Select proper command string based on arguments provided
        if label:
            if comment:
                command_string = 'commit label {0} comment {1}'.format(label, comment)
            elif confirm:
                command_string = 'commit label {0} confirmed {1}'.format(label, str(confirm_delay))
            else:
                command_string = 'commit label {0}'.format(label)
        elif confirm:
            command_string = 'commit confirmed {0}'.format(str(confirm_delay))
        elif comment:
            command_string = 'commit comment {0}'.format(comment)
        elif options:
            command_string = 'commit {0}'.format(options)
        else:
            command_string = 'commit'

        # Enter config mode (if necessary)
        output = self.config_mode()
        output += self.send_command_expect(command_string, strip_prompt=False, strip_command=False,
                                           delay_factor=delay_factor)
        if error_marker in output:
            raise ValueError("Commit failed with the following errors:\n\n{0}".format(output))

        return output

    def check_config_mode(self, check_string=')#', pattern=r"[#]"):
        """Checks if the device is in configuration mode or not.
        nso, does this:
        admin@ncs455_J2#
        """
        self.write_channel(self.RETURN)
        output = self.read_until_pattern(pattern=pattern)
        return check_string in output

    def config_mode(self, config_command='config term', pattern=''):
        """
        Enter into configuration mode on remote device.
        """
        if not pattern:
            pattern = re.escape(self.base_prompt[:16])
        return super().config_mode(config_command=config_command,
                                                            pattern=pattern)

    def exit_config_mode(self, exit_config='end'):
        """Exit configuration mode."""
        output = ''
        if self.check_config_mode():
            output = self.send_command_timing(exit_config, strip_prompt=False, strip_command=False)
            if "Uncommitted changes found" in output:
                output += self.send_command_timing('no', strip_prompt=False, strip_command=False)
            if self.check_config_mode():
                raise ValueError("Failed to exit configuration mode")
        return output

    def cleanup(self):
        """Gracefully exit the SSH session."""
        try:
            self.exit_config_mode()
        except Exception:
            # Always try to send 'end' regardless of whether exit_config_mode works or not.
            pass

