class Table(object):


    def __init__(self, fields=[], fields_sizes=[]):
        if len(fields) != len(fields_sizes):
            raise Exception("Fields and sizes have different length!")
        if not fields:
            raise Exception("No fields for the table!")
        self.fields = fields
        self.fields_sizes = fields_sizes
        self.rows = []
        

    def __str__(self):
        table_width = sum(self.fields_sizes) + len(self.fields) + 1
        s = ("-" * table_width) + "\n|"
        i = 0        
        while i < len(self.fields):
            if len(self.fields[i]) > self.fields_sizes[i]:
                raise Exception("Field size too low for column %d" % i)
            s += self.fields[i].ljust(self.fields_sizes[i], " ") + "|"
            i += 1
        s += "\n" + ("-" * table_width) + "\n|"
        if not self.rows:
            s = s[:-2]
            return s
        for row in self.rows:
            i = 0
            while i < len(self.fields):
                if len(row[i]) > self.fields_sizes[i]:
                    raise Exception("Field size too low for column %d" % i)
                s += row[i].ljust(self.fields_sizes[i], " ") + "|"
                i += 1
            s += "\n"
            s += ("-" * table_width) + "\n|"
        s = s[:-1]
        return s

    
    def add_row(self, row=[]):
        if len(self.fields) != len(row):
            raise Exception("Row fields are different from the header fields!")
        self.rows.append(row)


    