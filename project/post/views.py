from django.shortcuts import render

# Create your views here.

from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Post, Comment, Tag
from .serializers import PostSerializer, CommentSerializer

from django.shortcuts import get_object_or_404

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def list(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        queryset = self.filter_queryset(
            self.get_queryset().filter(post=post)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)

@api_view(['GET'])
def find_tag(request, tags_name):
    tags = get_object_or_404(Tag, name=tags_name)

    if request.method == 'GET':
        posts = Post.objects.filter(tags__in=[tags])
        serializer = PostSerializer(posts, many=True)
        return Response(data=serializer.data)