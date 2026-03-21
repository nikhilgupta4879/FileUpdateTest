from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate
from app.core.config import get_settings

settings = get_settings()


async def create_group(db: AsyncSession, owner_id: str, data: GroupCreate) -> Group:
    group = Group(name=data.name, owner_id=owner_id, is_public=data.is_public)
    db.add(group)
    member = GroupMember(group_id=group.id, user_id=owner_id)
    db.add(member)
    await db.commit()
    await db.refresh(group)
    return group


async def search_groups(db: AsyncSession, query: str) -> list[Group]:
    stmt = select(Group).where(Group.name.ilike(f"%{query}%"), Group.is_public.is_(True))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_member_count(db: AsyncSession, group_id: str) -> int:
    stmt = select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def join_group(db: AsyncSession, user_id: str, group_id: str) -> GroupMember:
    # Check not already member
    stmt = select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        return existing
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    await db.commit()
    return member


async def find_user_by_profile(db: AsyncSession, profile_name: str) -> User | None:
    stmt = select(User).where(User.profile_name == profile_name)
    return (await db.execute(stmt)).scalar_one_or_none()


async def toggle_favorite(db: AsyncSession, user_id: str, group_id: str) -> bool:
    stmt = select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    member = (await db.execute(stmt)).scalar_one_or_none()
    if not member:
        raise ValueError("Not a member of this group.")
    member.is_favorite = not member.is_favorite
    await db.commit()
    return member.is_favorite
