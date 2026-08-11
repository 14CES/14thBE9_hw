from django.shortcuts import render
# Create your views here.

from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action

from .models import Post, Comment, Tag
from .serializers import PostSerializer, PostListSerializer, CommentSerializer, TagSerializer

from django.shortcuts import get_object_or_404
from .permissions import IsWriterOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsWriterOrReadOnly
    ]

    def perform_create(self, serializer):
        post = serializer.save(writer=self.request.user)
        self.handle_tags(post)

    def perform_update(self, serializer):
        post = serializer.save()
        self.handle_tags(post)

    def handle_tags(self, post):
        post.tags.clear()

        words = post.content.split()

        tag_names = {
            word[1:].strip(',.!?')
            for word in words
            if word.startswith('#') and len(word) > 1
        }

        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            post.tags.add(tag)

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        
        return PostSerializer

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        post = (
            self.get_queryset()
            .order_by('?')
            .first()
        )

        if post is None:
            return Response(
                {
                    "detail": "등록된 영화가 없습니다."
                },
                status = status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(post)

        return Response(serializer.data)

    @action(methods=['GET'], detail=True)
    def test(self, request, pk=None):
        test_post = self.get_object()
        test_post.click_count += 1
        test_post.save(update_fields=['click_count'])
        return Response()

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)

        if request.user in post.like.all():
            post.like.remove(request.user)
            post.like_count -= 1
            post.save()

        else:
            post.like.add(request.user)
            post.like_count += 1
            post.save()

        return Response(PostSerializer(post).data)

    @action(detail=False, methods=['get'])
    def toplikes(self, request):
        posts = self.get_queryset().order_by('-like_count')[:3]

        serializer = self.get_serializer(posts, many=True)

        return Response(serializer.data)


class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsWriterOrReadOnly]

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = CommentSerializer
    permission_classes = [IsWriterOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')

        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id = post_id)
        serializer.save(
            post=post,
            writer=self.request.user,
        )

class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    lookup_field = 'name'
    lookup_url_kwarg = 'tag_name'

    def retrieve(self, request, *args, **kwargs):
        tag_name = kwargs.get('tag_name')
        tag = get_object_or_404(Tag, name = tag_name)

        posts = Post.objects.filter(tags=tag)
        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data)