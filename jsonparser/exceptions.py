def _calc_position(doc: str, pos: int) -> tuple:
    prefix = doc[:pos]
    lineno = prefix.count('\n') + 1
    colno  = pos - prefix.rfind('\n')
    return lineno, colno


class JSONDecodeError(ValueError):
    """JSON 파싱 실패 예외.

    Attributes:
        msg:    오류 설명 문자열
        doc:    파싱 중이던 원본 문자열
        pos:    오류 발생 위치 (문자 인덱스)
        lineno: 오류 발생 줄 번호 (1-based)
        colno:  오류 발생 열 번호 (1-based)
    """

    def __init__(self, msg: str, doc: str, pos: int):
        lineno, colno = _calc_position(doc, pos)
        self.msg    = msg
        self.doc    = doc
        self.pos    = pos
        self.lineno = lineno
        self.colno  = colno
        super().__init__(f"{msg}: line {lineno} column {colno} (char {pos})")
