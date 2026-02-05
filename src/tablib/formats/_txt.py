""" Tablib - Plain Text / Terminal Support.
"""

from io import StringIO


class TextFormat:
    title = 'text'
    extensions = ('txt',)

    DEFAULT_MAX_WIDTH = 80
    DEFAULT_PADDING = 2

    @classmethod
    def export_stream_set(cls, dataset, **kwargs):
        """Returns plain text representation of Dataset as file-like."""
        stream = StringIO()

        max_width = kwargs.get('max_width', cls.DEFAULT_MAX_WIDTH)
        padding = kwargs.get('padding', cls.DEFAULT_PADDING)

        if not dataset.headers:
            return stream

        # Calculate column widths
        col_widths = cls._calculate_column_widths(dataset, max_width, padding)

        # Write headers
        header_row = ' ' * padding + (' ' * padding).join(
            str(h)[:w].ljust(w) for h, w in zip(dataset.headers, col_widths)
        )
        stream.write(header_row.rstrip() + '\n')

        # Write separator
        separator = '-' * min(len(header_row), max_width)
        stream.write(separator + '\n')

        # Write data rows
        for row in dataset:
            data_row = ' ' * padding + (' ' * padding).join(
                str(cell)[:w].ljust(w) for cell, w in zip(row, col_widths)
            )
            stream.write(data_row.rstrip() + '\n')

        stream.seek(0)
        return stream

    @classmethod
    def export_set(cls, dataset, **kwargs):
        """Returns plain text representation of Dataset."""
        stream = cls.export_stream_set(dataset, **kwargs)
        return stream.getvalue()

    @classmethod
    def _calculate_column_widths(cls, dataset, max_width, padding):
        """Calculate optimal column widths."""
        if not dataset.headers:
            return []

        num_cols = len(dataset.headers)
        available_width = max_width - padding  # Account for initial padding

        # Calculate minimum width needed for each column
        min_widths = []
        for i, header in enumerate(dataset.headers):
            header_len = len(str(header))
            # Find max data width in this column
            data_max = max(
                (len(str(row[i])) for row in dataset if i < len(row)),
                default=0
            )
            min_widths.append(max(header_len, data_max, 3))  # Minimum 3 chars

        total_padding = padding * num_cols
        total_min = sum(min_widths) + total_padding

        if total_min <= available_width:
            # We have space, distribute extra evenly
            extra = available_width - total_min
            per_col = extra // num_cols
            return [w + per_col for w in min_widths]
        else:
            # Need to truncate - proportional distribution
            scale = (available_width - total_padding) / sum(min_widths)
            return [max(3, int(w * scale)) for w in min_widths]

    @classmethod
    def detect(cls, stream):
        """Returns True if given stream is valid plain text."""
        try:
            content = stream.read(1024)
            stream.seek(0)
            # Simple detection - if it decodes as text, we accept it
            if isinstance(content, bytes):
                content.decode('utf-8')
            return True
        except Exception:
            return False
