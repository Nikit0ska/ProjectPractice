from projectPractice.ConnThread import get_cursor

SQL_TEXT = 2000

SQL_CUSTOM_TYPES = {
    SQL_TEXT: None
}


def find_type_by_sqltype(sqltype):
    if sqltype >= 2000:
        return SQL_CUSTOM_TYPES[sqltype]
    else:
        type_info = [i[0] for i in get_cursor().getTypeInfo(sqltype)]
        # print(type_info)
        if len(type_info) == 1:
            return type_info[0]
        elif len(type_info) > 1:
            return type_info[0][0]