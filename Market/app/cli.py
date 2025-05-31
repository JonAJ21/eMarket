import asyncio
from functools import wraps
from uuid import uuid4
from typer import Typer
from faker import Faker
from random import choice, randint
from datetime import timedelta, datetime


from models.seller_info import SellerInfo
from schemas.social import SocialProvider
from models.social_account import SocialAccount
from models.user import User
from dependencies.services.user_role_service_factory import create_user_role_service
from dependencies.services.user_service_factory import create_user_service
from schemas.user import UserCreateDTO, UserDeviceType, UserHistoryCreateDTO, UserUpdatePersonalDTO
from db.postgres import get_session
from services.role import BaseRoleService
from dependencies.services.role_service_factory import create_role_service
from schemas.role import Roles
from schemas.role import RoleCreateDTO
from core.config import settings


cli = Typer()

def async_typer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

@cli.command()
@async_typer
async def init_roles():
    roles = [role.value for role in Roles.__members__.values()]
    try:
        session = get_session()
        role_service: BaseRoleService = create_role_service(session=session)
        for role in roles:
            dto: RoleCreateDTO = RoleCreateDTO(
                name=role,
                description=f"{role}"
            )
            role = await role_service.create_role(dto=dto)
            print(f"Role {role.name} created with ID {role.id}")
    except Exception as e:    
        print(e)

      
   

@cli.command()
@async_typer
async def init_superuser():    
    try:
        async with get_session() as session:
            user_service = create_user_service(session=session)
            user = await user_service.create_user(dto=UserCreateDTO(
                login=settings.super_user_login,
                password=settings.super_user_password,
            ))
            
            role_service = create_role_service(session=session)
            role = await role_service.get_role_by_name(name=Roles.SUPER_ADMIN.value)
            
            user_role_service = create_user_role_service(session=session)
            await user_role_service.assign_role_to_user(user.id, role.id)

            
            print(f"Superuser {user.login} created with ID {user.id}")
    except Exception as e:
        print(e)

@cli.command()
@async_typer
async def gen_postgres_data(rows: int = 100000, role_count: int = 3):
    try:
        
        fake = Faker('ru_RU')
        async with get_session() as session:
            user_service = create_user_service(session=session)
            role_service = create_role_service(session=session)
            user_role_service = create_user_role_service(session=session)
            
            for i in range(role_count):
                try:
                    await role_service.create_role(
                        dto=RoleCreateDTO(
                            name = fake.uid(),
                            description = fake.sentence()
                        )
                    )
                except Exception:
                    print("1")
                    continue
            await session.commit()
            roles = await role_service.get_roles(limit = rows)
            
            for i in range(rows):
                try:
                    user: User = await user_service.create_user(
                        dto=UserCreateDTO(
                            login='login' + str(uuid4()),
                            password=fake.password()
                        )
                    )
                except Exception:
                    print("2")
                    continue
                user.created_at = fake.date_time_this_century(before_now=True)
                user.updated_at = fake.date_time_between(
                    start_date=user.created_at,
                    end_date=user.created_at + timedelta(weeks=30)
                )
                
                await user_role_service.assign_role_to_user(
                    user_id=user.id,
                    role_id=choice(roles).id)
                
                
                while True:
                    try:
                        await user_service.update_personal(
                            dto=UserUpdatePersonalDTO(
                                user_id=user.id,
                                first_name=fake.first_name(),
                                last_name=fake.last_name(),
                                fathers_name=fake.middle_name(),
                                phone=fake.phone_number(),
                                email=str(uuid4()) + '@mail.om'
                            )
                        )
                    except Exception:
                        print('3')
                        continue
                    break
                
                social_providers = [SocialProvider.GOOGLE, SocialProvider.YANDEX]
                social_account_count = randint(0, 1)
                for i in range(social_account_count):
                    user.add_social_account(
                        social_account=SocialAccount(
                            user_id=user.id,
                            social_id=str(uuid4()),
                            social_name=choice(social_providers)
                        )
                    )
        
                is_seller = bool(randint(0, 1))
                if is_seller:
                    user.add_seller_info(
                        seller_info=SellerInfo(
                            user_id=user.id,
                            name=fake.word(),
                            address=fake.address(),
                            inn=fake.individuals_inn(),
                            payment_account=fake.numerify(text='#' * 20),
                            correspondent_account='301' + fake.numerify(text='#' * 17),
                            bank=fake.bank(),
                            bik=fake.bic(),
                            postal_code=fake.postcode(),
                            kpp=fake.kpp()
                        )
                    )
                    user.seller_info.created_at = fake.date_time_between(
                                start_date=user.created_at,
                                end_date=user.created_at + timedelta(weeks=30)
                            )
                    user.seller_info.updated_at = fake.date_time_between(
                                start_date=user.seller_info.created_at,
                                end_date=user.seller_info.created_at + timedelta(weeks=30)
                            )
                
                user_history_count = randint(0, 5)
                for i in range(user_history_count):
                    await user_service.insert_user_login(
                        dto=UserHistoryCreateDTO(
                            user_id=user.id,
                            user_agent=fake.user_agent(),
                            user_device_type=UserDeviceType.web.value,
                            attempted_at=fake.date_time_between(
                                start_date=user.created_at,
                                end_date=user.created_at + timedelta(weeks=30)
                            ),
                            is_success=bool(randint(0, 1))
                        )
                    )
                await session.commit() 
            await session.commit()
    except Exception as e:
        print(e)




if __name__ == "__main__":    
    cli()