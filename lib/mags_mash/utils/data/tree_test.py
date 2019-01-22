import pandas as pd

GOLD = pd.read_csv('GOLD-metadata.csv')
tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
            'Ecosystem Type','Specific Ecosystem','Project / Study Name']

def create_tree(GOLD, tree, tree_cols):
    if len(tree_cols) == 0:
        return tree
    col = tree_cols[0]
    type_count = GOLD[col].value_counts().to_dict()
    for t in type_count:
        if col == 'Ecosystem':
            print(tree_cols)
        tree.append({'name':t,'count':type_count[t], \
        'children': create_tree(GOLD[GOLD[col]==t], [], tree_cols[1:])})
    return tree

def show_tree(tree, layer):
    for t in tree:
        print(('  '*layer), t['name'], t['count'])
        show_tree(t['children'], layer+1)


GOLD = GOLD.fillna('Other')
tree = create_tree(GOLD, [], tree_cols)
show_tree(tree, 0)
