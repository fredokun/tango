"""The document generator produces an output document.
"""

from scriptex.markup import Markup

class GenerateError(Exception):
    pass

class DocumentGenerator:
    def __init__(self, document):
        self.document = document
        self.cmd_generators = dict()
        self.env_generators = dict()
        self.sec_generators = dict()
        
    def register_command_generator(self, cmd_name, cmd_generator):
        if cmd_name in self.cmd_generators:
            raise GenerateError("Generator for command {} already registered".format(cmd_name))

        self.cmd_generators[cmd_name] = cmd_generator

    def register_environment_generator(self, env_name, env_generator):
        if env_name in self.env_generators:
            raise GenerateError("Generator for environment {} already registered".format(env_name))

        self.env_generators[env_name] = env_generator

    def register_section_generator(self, sec_depth, sec_generator):
        if sec_depth in self.sec_generators:
            raise GenerateError("Generator for section level {}: already registered".format(sec_depth))

        if not self.sec_generators:
            self.sec_generators[0] = sec_generator # global generator if only one
        else:
            del self.sec_generators[0] # no global generator if more than one
            
        self.sec_generators[sec_depth] = sec_generator

        
    def generate(self):
        self.markup_stack = [(self.document, 0)]
        self.environment_stack = []
        self.command_stack = []
        self.section_stack = []

        while self.markup_stack:
            self.markup, self.content_index = self.markup_stack.pop()
            if self.content_index == -1: # command/env not generated
                if self.markup.markup_type == "command":
                    if self.markup.cmd_name in self.cmd_generators:
                        self.cmd_generators[self.markup.cmd_name].enter_command(self, self.markup)
                    self.command_stack.append(self.markup)
                elif self.markup.markup_type == "environment":
                    if self.markup.env_name in self.env_generators:
                        self.env_generators[self.markup.env_name].enter_environment(self, self.markup)
                    self.environment_stack.append(self.markup)
                elif self.markup.markup_type == "section":
                    if 0 in self.sec_generators:
                        self.sec_generators[0].enter_section(self, self.markup)
                    elif self.markup.section_depth in self.sec_generators:
                        self.sec_generators[self.markup.section_depth].enter_secton(self, self.markup)
                    self.section_stack.append(self.markup)
                # push back in queue but next time generate content at index 0 (first child)
                self.markup_stack.append((self.markup, 0))
            else: # generating of markup already started
                if self.content_index == len(self.markup.content):
                    # done generating content
                    if self.markup.markup_type == "command":
                        check_cmd = self.command_stack.pop()
                        assert check_cmd == self.markup,  "invalid command stack (please report)"
                        if self.markup.cmd_name in self.cmd_generators:
                            self.cmd_generators[self.markup.cmd_name].exit_command(self, self.markup)
                    elif self.markup.markup_type == "environment":
                        check_env = self.environment_stack.pop()
                        assert check_env == self.markup,  "invalid environment stack (please report)"
                        if self.markup.env_name in self.env_generators:
                            self.env_generators[self.markup.env_name].exit_environment(self, self.markup)
                    elif self.markup.markup_type == "section":
                        check_sec = self.section_stack.pop()
                        assert check_sec == self.markup, "Invalid section stack (please report)"
                        if 0 in self.sec_generators:
                            self.sec_generators[0].exit_section(self, self.markup)
                        elif self.markup.section_depth in self.sec_generators:
                           self.sec_generators[self.markup.section_depth].exit_section(self, self.markup)
                else: # generate a child
                    child = self.markup.content[self.content_index]
                    self.markup_stack.append((self.markup, self.content_index+1))
                    if isinstance(child, Markup):
                        self.markup_stack.append((child, -1))
                    else:
                        pass # XXX: generate non-markup content in some way ?

        # done generating



class CommandGenerator:
    def __init__(self):
        pass

    def enter_command(self, generating, cmd):
        pass # should be overriden

    def exit_command(self, generating, cmd):
        pass


class EnvironmentGenerator:
    def __init__(self):
        pass

    def enter_environment(self, generating, env):
        pass

    def exit_environment(self, generating, env):
        pass


class SectionGenerator:
    def __init__(self):
        pass

    def enter_section(self, generating, cmd):
        pass # should be overriden

    def exit_section(self, generating, cmd):
        pass
