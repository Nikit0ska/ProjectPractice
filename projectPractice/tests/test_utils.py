from projectPractice import Table


def assertTable(table_name, table_dict):
    created_table = Table(table_name)
    created_table_dict = created_table.columns
    print(created_table_dict)
    print(table_dict)
    for elem in created_table_dict:
        assert elem in table_dict
        if table_dict[elem]['column_type'] == "SERIAL":
            assert ('int' in created_table_dict[elem]['column_type'])
            assert created_table_dict[elem]['default_value'] is not None
            assert not created_table_dict[elem]['nullable']
        else:
            assert (created_table_dict[elem]['column_type'] in table_dict[elem][
                'column_type'] or
                    table_dict[elem]['column_type'] in created_table_dict[elem]['column_type'])

            assert (created_table_dict[elem]['nullable'] == table_dict[elem]['nullable'])
            assert (created_table_dict[elem]['default_value'] is not None and table_dict[elem][
                'default_value'] is not None) or \
                   (created_table_dict[elem]['default_value'] is None and table_dict[elem][
                       'default_value'] is None)