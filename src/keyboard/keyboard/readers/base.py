from abc import ABC, abstractmethod


class KeyboardReaderBase(ABC):
    """
    キーボード入力バックエンドの共通インターフェース．
    """

    @abstractmethod
    def snapshot(self) -> list[str]:
        """
        現在押されているキー一覧を返す．
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """
        終了処理を行う．
        """
        raise NotImplementedError