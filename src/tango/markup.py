
class AbstractMarkup:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        
    def toxml(self, indent_level=0, indent_string=""):
        raise NotImplementedError("Abstract method")

    def pos_toxml(self, pos_name, pos):
        if pos is None:
            return ""
        return '{}="{}"'.format(pos_name, str(pos))

    def positions_toxml(self):
        return '{} {}'.format(self.pos_toxml("start_pos", self.start_pos), self.pos_toxml("end_pos", self.end_pos))

class Markup(AbstractMarkup):
    def __init__(self, markup_type, start_pos, end_pos):
        super().__init__(start_pos, end_pos)
        self.markup_type = markup_type

        self.content = []

    def content_toxml(self, indent_level=0, indent_string="  "):
        #return "".join((element.toxml(indent_level + 1, indent_string) if isinstance(element,AbstractMarkup) else str(element) for element in self.content))
        return "".join((element.toxml(indent_level + 1, indent_string) for element in self.content))


    def append(self, element):
        self.content.append(element)

class Document(Markup):
    def __init__(self, filename, start_pos):
        super().__init__("document", start_pos, None)
        self.filename = filename
        self.section_depth = 0  # document has minimal depth

    def __repr__(self):
        return "Document(content={})".format(repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<document filename="{}" {}>\n'.format(self.filename, self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + '</document>\n'
        return ret

class Command(Markup):
    def __init__(self, cmd_name, cmd_opts, header_start_pos, header_end_pos, preformated=False):
        super().__init__("command", header_start_pos, header_end_pos)
        self.cmd_name = cmd_name
        self.cmd_opts = cmd_opts
        self.header_end_pos = header_end_pos
        self.preformated = preformated

    def __repr__(self):
        return "Command(cmd_name={}, cmd_opts={}, preformated={}, content={})".format(self.cmd_name, self.cmd_opts, self.preformated, repr(self.content))

    def opts_toxml(self):
        return '"{}"'.format(self.cmd_opts)

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<command name="{}" opts={} preformated="{}" {} >\n'.format(self.cmd_name, self.opts_toxml(), str(self.preformated), self.positions_toxml())
        if self.preformated:
            ret += "".join(((indent_string * (indent_level + 1)) + line + "\n" for line in self.content.splitlines()))
        else:
            ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</command>\n"
        return ret

class Environment(Markup):
    def __init__(self, env_name, env_opts, header_start_pos, header_end_pos):
        super().__init__("environment", header_start_pos, None)
        self.env_name = env_name
        self.env_opts = env_opts
        self.header_end_pos = header_end_pos

    def __repr__(self):
        return "Environment(env_name={},env_opts={},content={})".format(self.env_name, self.env_opts, repr(self.content))

    def opts_toxml(self):
        return '"{}"'.format(self.env_opts)

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<environment name="{}" opts={} {} >\n'.format(self.env_name, self.opts_toxml(), self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</environment>\n"
        return ret


class Section(Markup):
    def __init__(self, section_title, section_name, section_depth, header_start_pos, header_end_pos):
        super().__init__("section", header_start_pos, None)
        self.section_title = section_title
        self.section_name = section_name
        self.section_depth = section_depth
        self.header_end_pos = header_end_pos

    def __repr__(self):
        return "Section(section_title={},section_name={},section_depth={},content={})".format(self.section_title, self.section_name, self.section_depth, repr(self.content))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<section title="{}" name="{}" depth="{}" {} >\n'.format(self.section_title, self.section_name, str(self.section_depth), self.positions_toxml())
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</environment>\n"
        return ret


class Text(AbstractMarkup):
    def __init__(self, text, start_pos, end_pos):
        super().__init__(start_pos, end_pos)
        self.text = text

    def __repr__(self):
        return 'Text("{}")'.format(self.text)

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<text {}>{}</text>\n'.format(self.positions_toxml(), self.text)
        return ret


class Preformated(AbstractMarkup):
    def __init__(self, text, lang, start_pos, end_pos):
        super().__init__(start_pos, end_pos)
        self.text = text
        self.lang = lang

    def __repr__(self):
        return 'Preformated("{}")'.format(self.text)
    
    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<preformated lang="{}" {} >\n'.format(self.cmd_name, self.positions_toxml())
        ret += "".join(((indent_string * (indent_level + 1)) + line + "\n" for line in self.text.splitlines()))
        ret += self.content_toxml(indent_level + 1, indent_string)
        ret += (indent_string * indent_level) + "</preformated>\n"
        return ret

class Newlines(AbstractMarkup):
    def __init__(self, newlines, start_pos, end_pos):
        super().__init__(start_pos, end_pos)
        self.newlines = newlines

    def __repr__(self):
        return "Newlines({})".format(len(self.newlines))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<newline count="{}" {} />\n'.format(len(self.newlines), self.positions_toxml())
        return ret


class Spaces(AbstractMarkup):
    def __init__(self, spaces, start_pos, end_pos):
        super().__init__(start_pos, end_pos)
        self.spaces = spaces

    def __repr__(self):
        return "Spaces({})".format(len(self.spaces))

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<space count="{}" {} />\n'.format(len(self.spaces), self.positions_toxml())
        return ret

class SkipMarkup(AbstractMarkup):
    def __init__(self, start_pos, end_pos):
        super().__init__(start_pos, end_pos)

    def __repr__(self):
        return "SkipMarkup()"

    def toxml(self, indent_level=0, indent_string="  "):
        ret = indent_string * indent_level
        ret += '<skip {} />\n'.format(self.positions_toxml())
        return ret