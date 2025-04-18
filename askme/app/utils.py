from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.core.paginator import Page


def paginate(request: HttpResponse, objects: QuerySet, per_page: int = 5) -> Page:
    paginator = Paginator(objects, per_page)
    page = request.GET.get("page", 1)

    try:
        paginated_objects = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_objects = paginator.page(1)

    return paginated_objects
