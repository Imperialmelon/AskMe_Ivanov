from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate(request, objects, per_page=5):
    paginator = Paginator(objects, per_page)  
    page = request.GET.get('page', 1)
    
    try:
        paginated_objects = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_objects = paginator.page(1)
 
    return paginated_objects
