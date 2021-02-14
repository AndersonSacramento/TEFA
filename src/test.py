from nltk.corpus import framenet as fn
from rich.console import Console


if __name__ == '__main__':
    console = Console()
    test_data = [
        {"jsonrpc": "2.0", "method": "sum", "params": [None, 1, 2, 4, False, True], "id": "1",},
        {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
        {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2"},
    ]

    def test_log():
        enabled = False
        context = {
        "foo": "bar",
    }
        movies = ["Deadpool", "Rise of the Skywalker"]
        console.log("Hello from", console, "!")
        console.log(test_data, log_locals=True)


    test_log()
    revenge = fn.frame('Revenge')
    revenge.frameRelations[0]
    fe_avenger = revenge.FE['Avenger']
    assert fe_avenger.coreType == 'Core'
    fe_degree = revenge.FE['Degree']
    assert fe_degree.coreType == 'Peripheral'
    if relation.type.name == 'Inheritance' and relation.name == 'Event'
        


