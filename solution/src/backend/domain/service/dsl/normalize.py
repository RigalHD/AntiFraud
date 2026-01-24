from backend.domain.service.dsl.ast_node import ASTNode, Comparison, Logical


def normalize_ast(node: ASTNode) -> ASTNode:
    if isinstance(node, Logical):
        left = normalize_ast(node.left)
        right = normalize_ast(node.right)
        operator = node.operator.upper()

        if isinstance(left, Logical) and left.operator == operator:
            return Logical(
                left=left.left,
                operator=operator,
                right=Logical(left=left.right, operator=operator, right=right),
            )

        return Logical(left=left, operator=operator, right=right)

    return node


def ast_to_string(node: ASTNode) -> str:
    if isinstance(node, Comparison):
        right = node.right

        if isinstance(right, str):
            right = f"'{right}'"

        return f"{node.left} {node.operator} {right}"

    return f"{ast_to_string(node.left)} {node.operator} {ast_to_string(node.right)}"
