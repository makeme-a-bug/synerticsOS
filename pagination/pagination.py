from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



#patterm ?page_size=10&page=2
#issue: shows all pages when page_size is set to 0
class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'last_page': self.page.paginator.num_pages,
            'results': data,
            'page_size': self.page.paginator.per_page
        })




#pagination function for custom action in viewsets
def response_with_paginator(viewset, queryset):
    page = viewset.paginate_queryset(queryset)
    if page is not None:
        serializer = viewset.get_serializer(page, many=True)
        return viewset.get_paginated_response(serializer.data)

    return Response(viewset.get_serializer(queryset, many=True).data)