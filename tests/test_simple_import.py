from .base import BaseImportTestCase


class ImportTestCase(BaseImportTestCase):
    serializer_name = 'tests.data_app.wizard.SimpleSerializer'

    def test_manual(self):
        run = self.upload_file('simplemodel.csv')

        # Inspect unmatched columns and select choices
        self.check_columns(run, 3, 1)
        self.update_columns(run, {
            'Simple Model': {
                'field notes': 'notes'
            }
        })

        # Start data import process, wait for completion
        self.start_import(run, [{
            'row': 5,
            'reason': "{'color': ['\"orange\" is not a valid choice.']}"
        }, {
            'row': 6,
            'reason': "{'date': ['Date has wrong format."
                      " Use one of these formats instead: YYYY[-MM[-DD]].']}"
        }])

        # Verify results
        self.check_data(run)
        self.assert_log(run, [
            'created',
            'parse_columns',
            'update_columns',
            'do_import',
            'import_complete',
        ])

    def test_auto(self):
        # Should abort since "field notes" is not mapped
        run = self.upload_file('simplemodel.csv')
        self.auto_import(run, expect_input_required=True)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
        ])

    def test_auto_preset(self):
        # Initialize identifier before auto import
        self.create_identifier('field notes', 'notes')

        # Should succeed since field notes is already mapped
        run = self.upload_file('simplemodel.csv')
        self.auto_import(run, expect_input_required=False)

        # Verify results
        self.check_data(run)
        self.assert_log(run, [
            'created',
            'auto_import',
            'parse_columns',
            'parse_row_identifiers',
            'do_import',
            'import_complete',
        ])

    def check_data(self, run):
        self.assert_status(run, 3)
        self.assert_ranges(run, [
            "Data Column 'date -> date' at Rows 1-5, Column 0",
            "Data Column 'color -> color' at Rows 1-5, Column 1",
            "Data Column 'field notes -> notes' at Rows 1-5, Column 2",
        ])
        self.assert_records(run, [
            "imported '2017-06-01: red (Test Note 1)' at row 1",
            "imported '2017-06-02: green (Test Note 2)' at row 2",
            "imported '2017-06-03: blue (Test Note 3)' at row 3",
            "failed at row 4:"
            " {'color': ['\"orange\" is not a valid choice.']}",
            "failed at row 5:"
            " {'date': ['Date has wrong format."
            " Use one of these formats instead: YYYY[-MM[-DD]].']}"
        ])