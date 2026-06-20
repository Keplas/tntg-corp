"""
Bulk image upload view — staff only.
Accessible at /admin/upload-images/
Allows selecting multiple images at once; auto-matches to products.
"""
import os, json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.views.decorators.http import require_http_methods
from marketplace.models import Product


def _match_product(filename):
    """Match a filename to a product. Returns Product or None."""
    stem = os.path.splitext(filename)[0]

    # product_<id> pattern
    if stem.lower().startswith('product_'):
        try:
            pk = int(stem.split('_', 1)[1])
            return Product.objects.get(pk=pk)
        except (ValueError, Product.DoesNotExist):
            pass

    # Name-based match (underscores = spaces)
    search = stem.replace('_', ' ').replace('-', ' ').lower()
    for p in Product.objects.all():
        if search in p.name.lower() or p.name.lower() in search:
            return p
    return None


@staff_member_required
def image_upload_page(request):
    """Render the bulk upload page."""
    products = Product.objects.order_by('category', 'name').values(
        'id', 'name', 'category', 'image'
    )
    use_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)
    ctx = {
        'products': list(products),
        'use_cloudinary': use_cloudinary,
        'title': 'Bulk Image Upload',
    }
    return render(request, 'admin/image_upload.html', ctx)


@staff_member_required
@csrf_exempt
@require_http_methods(['POST'])
def image_upload_api(request):
    """
    Handle single image upload + product assignment.
    Called via AJAX from the upload page.
    Expects: multipart/form-data with 'image' file and 'product_id'
    """
    image_file = request.FILES.get('image')
    product_id = request.POST.get('product_id')

    if not image_file:
        return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
    if not product_id:
        return JsonResponse({'success': False, 'error': 'No product selected'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

    use_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)

    if use_cloudinary:
        # Upload to Cloudinary
        try:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                image_file,
                folder        = 'tntg/products',
                public_id     = f'product_{product.pk}',
                overwrite     = True,
                resource_type = 'image',
                transformation = [{'quality': 'auto', 'fetch_format': 'auto'}],
            )
            product.image = result['public_id']
            product.save(update_fields=['image'])
            image_url = result['secure_url']
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        # Save locally (development mode)
        product.image = image_file
        product.save(update_fields=['image'])
        try:
            image_url = product.image.url
        except Exception:
            image_url = '/media/' + str(product.image)

    return JsonResponse({
        'success': True,
        'product_id':   product.pk,
        'product_name': product.name,
        'image_url':    image_url,
        'storage':      'cloudinary' if use_cloudinary else 'local',
    })


@staff_member_required
@csrf_exempt
@require_http_methods(['POST'])
def image_auto_match(request):
    """
    Auto-match uploaded filename to a product and return the match.
    Expects JSON: {"filename": "samsung_tv.jpg"}
    """
    try:
        data     = json.loads(request.body)
        filename = data.get('filename', '')
        product  = _match_product(filename)
        if product:
            return JsonResponse({
                'matched': True,
                'product_id':   product.pk,
                'product_name': product.name,
                'category':     product.get_category_display(),
            })
        return JsonResponse({'matched': False})
    except Exception as e:
        return JsonResponse({'matched': False, 'error': str(e)})


@staff_member_required
def product_thumb_url(request, product_id):
    """Return the current image URL for a product (used by the upload page JS)."""
    try:
        product = Product.objects.get(pk=product_id)
        if product.image:
            url = product.image.url
            return JsonResponse({'url': url})
        return JsonResponse({'url': None})
    except Exception:
        return JsonResponse({'url': None})
