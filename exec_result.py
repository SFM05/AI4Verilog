class ExecResult:
    def __init__(self,
                 input,
                 output,
                 cache_read,
                 cache_write,
                 ses_id):
        self.input = input
        self.output = output
        self.cache_read = cache_read
        self.cache_write = cache_write
        self.ses_id = ses_id

    def __str__(self):
        if self.input is not None and \
            self.output is not None and \
            self.cache_read is not None and \
            self.cache_write is not None:
            s = f'{self.input+self.cache_read:>12} {self.output+self.cache_write:>12}'
        else:
            s = f'{'N/A':>12} {'N/A':>12}'

        if self.ses_id:
            s += f'    {self.ses_id}'
        else:
            s += '     Unknwon'

        return s
