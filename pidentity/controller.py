from pidentity.macros import Operation, OPERATIONS



class Controller(object):
    def __init__(self, conditions):
        self.__ctrl = conditions.control
        self.__conditions = conditions
        self.__stores = {}  # determine on which to keep and which to throw away

    def __extract(self, pathway):
        print('We saw ourself here in the field: ', pathway)
        print('*' * 50)
        pathways = pathway.split('.')
        data = self.__stores
        for part in pathways:
            data = data.get(part)
        return data

    def __parse_rule_key(self, key):
        logic = key[0]
        field = key[1:-3]
        op = OPERATIONS.get(key[-3:])
        return logic, field, op

    def __parse_rule_value(self, field):
        prefix = field.split('.')[0]
        if prefix in ['$content', '$context', '$contact']:
            return field, None
        return None, field

    def content(self, values: dict):
        self.__stores['$content'] = values
        return self

    def context(self, values: dict):
        self.__stores['$context'] = values
        return self

    def contact(self, values: dict):
        self.__stores['$contact'] = values
        return self

    def evaluator(self, rules, data):
        """
        Evaluate the condition i.e. {
            '&id:==': '132313122',
            '&name:==': 'John Doe',
            '&age:==': 18,
            '&location@==': '$context.location',
            '&reference@??': '$contact.id',
            '&address:::': {
                '&city:==': 'New York',
                '&state:==': 'NY',
            }
        }
        
        1. get the key so we can expand it
            - &id:== will be expanded into key, op where op is <type, equals: Callable> and key = &id
            the key &reference@?? will be op <type, Callable: refs('contact.id', op: Callable)>
        
        2. extract the values from the data to run the ops upon

        # Content Evaluation
        {
            '@': lambda (k: string): return 
            ':': lambda k: 
        }
        """
        for key, value in rules.items():
            # logic = & || or, field = key i.e. id, operator = Operator() instance
            logic, field, operation = self.__parse_rule_key(key)

            # reference == $lookup path or None, datum is the actual data or the $store i.e. context, content etc if reference is True
            # if actual value we keep it to be used in comparison operation
            # if it is a reference then get the actual value to be used in comparison operation
            reference, value_in_rules = self.__parse_rule_value(value)
            if reference: value_in_rules = self.__extract(reference)
                    
            # check if the field passes validation for the commensurate rules
            value_in_data = data.get(field)
            if (not value_in_data) and (logic == '&'): return False
            if (not operation(value_in_rules, value_in_data)) and (logic == '&'): return False
        return True
    
    def go(self) -> bool:
        conditions, good = [], []
        that = self.__conditions
        for o in ['$content', '$context', '$contact']:
            data = self.__stores.get(o)
            if(data):
                # get the rules / conditions from memory or storage and log it
                rules = {'$content': that.content, '$context': that.context, '$contact': that.contact}.get(o)
                if not rules: continue
                conditions.append((rules, data))

        if not conditions: return False
        for condition in conditions:
            rules, data = condition
            good.append(self.evaluator(rules = rules, data = data))

        return all(good)


