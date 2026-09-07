import enum
from sqlalchemy import func, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from datetime import datetime

class MediaStatus(enum.Enum):
    PROCESSING = "processing"
    FAILED = "failed"
    UPLOADED = "uploaded"
    READY = "ready"

class MediaType(enum.Enum):
    VIDEO = "video"
    IMAGE = "image"


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True,nullable=False)
    username: Mapped[str] = mapped_column(unique=True,nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

class Follows(Base):
    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),nullable=False)

    __table_args__ = (
        CheckConstraint(
            "follower_id != following_id",
            name="check_user_cannot_follow_self"
        ),
    )

class Posts(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True,nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False
    )
    caption: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),nullable=False)

    media: Mapped[list["PostMedia"]] = relationship(
        back_populates = "post"
    )

class PostMedia(Base):
    __tablename__ = "postmedia"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id")
    )
    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType),
        nullable=False
    )
    storage_path: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[MediaStatus] = mapped_column(
        Enum(MediaStatus),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),nullable=False)

    post: Mapped["Posts"] = relationship(
        back_populates="media"
    )

class Likes(Base):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        primary_key=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(),nullable=False)