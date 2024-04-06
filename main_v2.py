import json

from graphs.RebusGraphParser import RebusGraphParser
from graphs.RebusImageConverter import RebusImageConverter

rebus_parser = RebusGraphParser("./saved/ladec_raw_small.csv")
image_converter = RebusImageConverter()

graph = rebus_parser.parse_compound("foreground")[0]
print(graph)
image_converter.convert_graph_to_image(graph, show=True)

# graph = rebus_parser.parse_compound(c1="to", c2="die", is_plural=False)[0]
# print(graph)

# with open("./saved/idioms_raw.json", "r") as file:
#     idioms = json.load(file)
#     for idiom in idioms:
#         try:
#             graph = rebus_parser.parse_idiom(idiom)
#             if graph is not None:
#                 print(idiom)
#                 print(graph)
#                 image_converter.convert_graph_to_image(graph, show=True)
#         except:
#             print(f"ERROR: '{idiom}'")

# graph = rebus_parser.parse_idiom("go back in time")
# print(graph)
# image_converter.convert_graph_to_image(graph, show=True)

# graph = rebus_parser.parse_compound(c1="two", c2="for", is_plural=False)[1]
# print(graph)
