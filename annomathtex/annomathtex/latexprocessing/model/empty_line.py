from .token import Token


"""
Needed to treat empty lines
"""

class EmptyLine(Token):

    def __init__(self, unique_id, type='Emptyline', highlight=None, content=None, endline=True, wikidata_result=None):
        """
        Constructor of superclass Token is called for highlight and content

        :param unique_id: uuid.uuid1 object, converted to a string. Needed in template for rendering.
        :param type: String, "Word","Identifier" or "Emptyline". Needed for correct template rendering
        :param highlight: String, colour, that the Identifier should be highlighted in. None if no highlight desired.
        :param content: String, The Identifier itself.
        :param endline: Boolean, needed for page rendering
        """
        super().__init__(unique_id, type, highlight, content, endline, wikidata_result)

    def get_unique_id(self):
        """
        Get the unique id of the emptyline

        Can I remove this method for empty line?

        :return: String of unique id
        """
        return self.unique_id

    def get_type(self):
        """
        Get the name of the current class.
        :return: Name of class.
        """
        return self.type

    def get_highlight(self):
        """
        Get the highlight value for the Word.
        :return: Colour of highlighting, None if no highlighting.
        """
        return self.highlight

    def get_content(self):
        """
        Get the word itself.
        :return: String of word
        """
        return self.content

    def get_endline(self):
        """
        Get the boolean value.
        :return: endline, true or false
        """
        return self.endline

    def set_endline(self, new_endline_val):
        """
        set the endline value
        :param new_endline_val:
        :return: None
        """
        self.endline = new_endline_val
