from rewrite.test import rewrite_run, python


# @Test
#     void simple() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case 1:
#                     pass
#                 case 2:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void wildcard() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case 1:
#                     pass
#                 case 2:
#                     pass
#                 case _:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void sequence() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case [1, 2]:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void star() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case [1, 2, *rest]:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void guard() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case [1, 2, *rest] if 42 in rest:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void or() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case 2 | 3:
#                     pass
#               """
#           )
#         );
#     }
#
#     @ParameterizedTest
#     @ValueSource(strings = {
#       "",
#       "a",
#       "b, c",
#       "a, b=c",
#       "a, b=c, d=(e,f)",
#     })
#     void className(String args) {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case ClassName(%s):
#                     pass
#               """.formatted(args)
#           )
#         );
#     }
#
#     @Test
#     void mapping() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case {"x": x, "y": y, **z}:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void value() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case value.pattern:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void nested() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case [int(), str()]:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void as() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case [int(), str()] as y:
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void group() {
#         rewriteRun(
#           python(
#             """
#               match x:
#                 case (value.pattern):
#                     pass
#               """
#           )
#         );
#     }
#
#     @Test
#     void sequenceTarget() {
#         rewriteRun(
#           python(
#             """
#               match x, y:
#                 case a, b:
#                     pass
#               """
#           )
#         );
#     }

def test_simple():
    # language=python
    rewrite_run(
        python(
            """\
            def test(x):
                match x:
                    case 1:
                        pass
                    case 2:
                        pass
            """
        )
    )
