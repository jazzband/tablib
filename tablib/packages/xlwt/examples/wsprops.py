props = \
[
        'name',
        'parent',
        'rows',
        'cols',
        'merged_ranges',
        'bmp_rec',
        'show_formulas',
        'show_grid',
        'show_headers',
        'panes_frozen',
        'show_empty_as_zero',
        'auto_colour_grid',
        'cols_right_to_left',
        'show_outline',
        'remove_splits',
        'selected',
        'hidden',
        'page_preview',
        'first_visible_row',
        'first_visible_col',
        'grid_colour',
        'preview_magn',
        'normal_magn',
        'row_gut_width',
        'col_gut_height',
        'show_auto_page_breaks',
        'dialogue_sheet',
        'auto_style_outline',
        'outline_below',
        'outline_right',
        'fit_num_pages',
        'show_row_outline',
        'show_col_outline',
        'alt_expr_eval',
        'alt_formula_entries',
        'row_default_height',
        'col_default_width',
        'calc_mode',
        'calc_count',
        'RC_ref_mode',
        'iterations_on',
        'delta',
        'save_recalc',
        'print_headers',
        'print_grid',
        'grid_set',
        'vert_page_breaks',
        'horz_page_breaks',
        'header_str',
        'footer_str',
        'print_centered_vert',
        'print_centered_horz',
        'left_margin',
        'right_margin',
        'top_margin',
        'bottom_margin',
        'paper_size_code',
        'print_scaling',
        'start_page_number',
        'fit_width_to_pages',
        'fit_height_to_pages',
        'print_in_rows',
        'portrait',
        'print_not_colour',
        'print_draft',
        'print_notes',
        'print_notes_at_end',
        'print_omit_errors',
        'print_hres',
        'print_vres',
        'header_margin',
        'footer_margin',
        'copies_num',
]

from xlwt import *

wb = Workbook()
ws = wb.add_sheet('sheet')

print ws.name
print ws.parent
print ws.rows
print ws.cols
print ws.merged_ranges
print ws.bmp_rec
print ws.show_formulas
print ws.show_grid
print ws.show_headers
print ws.panes_frozen
print ws.show_empty_as_zero
print ws.auto_colour_grid
print ws.cols_right_to_left
print ws.show_outline
print ws.remove_splits
print ws.selected
# print ws.hidden
print ws.page_preview
print ws.first_visible_row
print ws.first_visible_col
print ws.grid_colour
print ws.preview_magn
print ws.normal_magn
#print ws.row_gut_width
#print ws.col_gut_height
print ws.show_auto_page_breaks
print ws.dialogue_sheet
print ws.auto_style_outline
print ws.outline_below
print ws.outline_right
print ws.fit_num_pages
print ws.show_row_outline
print ws.show_col_outline
print ws.alt_expr_eval
print ws.alt_formula_entries
print ws.row_default_height
print ws.col_default_width
print ws.calc_mode
print ws.calc_count
print ws.RC_ref_mode
print ws.iterations_on
print ws.delta
print ws.save_recalc
print ws.print_headers
print ws.print_grid
#print ws.grid_set
print ws.vert_page_breaks
print ws.horz_page_breaks
print ws.header_str
print ws.footer_str
print ws.print_centered_vert
print ws.print_centered_horz
print ws.left_margin
print ws.right_margin
print ws.top_margin
print ws.bottom_margin
print ws.paper_size_code
print ws.print_scaling
print ws.start_page_number
print ws.fit_width_to_pages
print ws.fit_height_to_pages
print ws.print_in_rows
print ws.portrait
print ws.print_colour
print ws.print_draft
print ws.print_notes
print ws.print_notes_at_end
print ws.print_omit_errors
print ws.print_hres
print ws.print_vres
print ws.header_margin
print ws.footer_margin
print ws.copies_num
