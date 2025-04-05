from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from application.models import Listing, Review, db
from application.forms import ListingForm, ReviewForm
from datetime import datetime

marketplace_bp = Blueprint('marketplace', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@marketplace_bp.route('/marketplace')
def marketplace():
    listings = Listing.query.order_by(Listing.created_at.desc()).all()
    return render_template('marketplace/marketplace.html', listings=listings)

@marketplace_bp.route('/marketplace/add', methods=['GET', 'POST'])
@login_required
def add_listing():
    form = ListingForm()
    if form.validate_on_submit():
        # Handle file upload
        image_file = form.image.data
        filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            filename = f"uploads/{filename}"
        
        listing = Listing(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image=filename,
            location=form.location.data,
            user_id=current_user.id
        )
        db.session.add(listing)
        db.session.commit()
        flash('Your listing has been added!', 'success')
        return redirect(url_for('marketplace.marketplace'))
    return render_template('marketplace/add_listing.html', form=form)

@marketplace_bp.route('/marketplace/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    reviews = Review.query.filter_by(listing_id=listing_id).order_by(Review.created_at.desc()).all()
    form = ReviewForm()
    return render_template('marketplace/listing_detail.html', 
                         listing=listing, reviews=reviews, form=form)

@marketplace_bp.route('/marketplace/<int:listing_id>/review', methods=['POST'])
@login_required
def add_review(listing_id):
    form = ReviewForm()
    listing = Listing.query.get_or_404(listing_id)
    
    if form.validate_on_submit():
        # Check if user already reviewed this listing
        existing_review = Review.query.filter_by(
            user_id=current_user.id, 
            listing_id=listing_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this listing', 'warning')
            return redirect(url_for('marketplace.listing_detail', listing_id=listing_id))
        
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            listing_id=listing_id
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been added!', 'success')
    
    return redirect(url_for('marketplace.listing_detail', listing_id=listing_id))

@marketplace_bp.route('/marketplace/my_listings')
@login_required
def my_listings():
    listings = Listing.query.filter_by(user_id=current_user.id)\
        .order_by(Listing.created_at.desc()).all()
    return render_template('marketplace/my_listings.html', listings=listings)

@marketplace_bp.route('/marketplace/delete/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    
    if listing.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to delete this listing', 'danger')
        return redirect(url_for('marketplace.marketplace'))
    
    # Delete associated reviews
    Review.query.filter_by(listing_id=listing_id).delete()
    
    # Delete the listing
    db.session.delete(listing)
    db.session.commit()
    flash('Your listing has been deleted', 'success')
    return redirect(url_for('marketplace.marketplace'))