      subroutine find_feature_3b_type1(natom,itype_atom,Rc,Rc2,n3b1,n3b2, &
        num_neigh,list_neigh, &
        dR_neigh,iat_neigh,ntype,grid31,grid32, &
        feat_all,dfeat_allR,nfeat0m,m_neigh,n3b1m,n3b2m,nfeat_atom)
      implicit none
      integer ntype
      integer natom,n3b1(ntype),n3b2(ntype)
      integer m_neigh
      integer itype_atom(natom)
      real*8 Rc(ntype),Rc2(ntype)
      real*8 dR_neigh(3,m_neigh,ntype,natom)
      real*8 dR_neigh_alltype(3,m_neigh,natom)
      integer iat_neigh(m_neigh,ntype,natom),list_neigh(m_neigh,ntype,natom)
      integer num_neigh(ntype,natom)
      integer num_neigh_alltype(natom)
      integer nperiod(3)
      integer iflag,i,j,num,iat,itype
      integer i1,i2,i3,itype1,itype2,j1,j2,iat1,iat2
      real*8 d,dx1,dx2,dx3,dx,dy,dz,dd
      real*8 grid31(0:n3b1m+1,ntype),grid32(0:n3b2m+1,ntype)
      real*8 pi,pi2,x,f1
      integer iflag_grid
      integer itype0,nfeat0m,n3b1m,n3b2m

      real*8 feat3(n3b1m*n3b1m*n3b2m,ntype*(ntype+1)/2,natom)
      real*8 dfeat3(n3b1m*n3b1m*n3b2m,ntype*(ntype+1)/2,natom,m_neigh,3)

      real*8 feat3_tmp(2,m_neigh,ntype)
      real*8 dfeat3_tmp(2,m_neigh,ntype,3)
      integer ind_f(2,m_neigh,ntype,natom)
      real*8 f32(2),df32(2,2,3)
      integer inf_f32(2),k,k1,k2,k12,j12,ii_f,jj,jj1,jj2,nneigh,ii
      real*8 y,y2
      integer itype12,ind_f32(2)
      integer ind_all_neigh(m_neigh,ntype,natom),list_neigh_alltype(m_neigh,natom)

      real*8 feat_all(nfeat0m,natom),dfeat_allR(nfeat0m,natom,m_neigh,3)
      real*8 dfeat_all(nfeat0m,natom,m_neigh,3)
      integer nfeat_atom(natom)


      num_neigh_alltype=0
      do iat=1,natom
      num=1
      list_neigh_alltype(1,iat)=iat   ! the first neighbore is itself
      dR_neigh_alltype(:,1,iat)=0.d0

      do  itype=1,ntype
      do   j=1,num_neigh(itype,iat)


      num=num+1
        if(num.gt.m_neigh) then
        write(6,*) "Error! maxNeighborNum too small",m_neigh
        stop
        endif
      ind_all_neigh(j,itype,iat)=num
      list_neigh_alltype(num,iat)=list_neigh(j,itype,iat)
      dR_neigh_alltype(:,num,iat)=dR_neigh(:,j,itype,iat)
      enddo
      enddo
      num_neigh_alltype(iat)=num
      enddo

!ccccccccccccccccccccccccccccccccccccccccc

      pi=4*datan(1.d0)
      pi2=2*pi

      feat3=0.d0
      dfeat3=0.d0


      do 3000 iat=1,natom
       itype0=itype_atom(iat)

      do 1000 itype=1,ntype
      do 1000 j=1,num_neigh(itype,iat)

      jj=ind_all_neigh(j,itype,iat)

      dd=dR_neigh(1,j,itype,iat)**2+dR_neigh(2,j,itype,iat)**2+dR_neigh(3,j,itype,iat)**2
      d=dsqrt(dd)


      do k=1,n3b1(itype0)+1
      if(grid31(k,itype0).ge.d) exit
      enddo
      k=k-1

      if(k.gt.n3b1(itype0))  k=n3b1(itype0)

      if(k.lt.n3b1(itype0)) then
      x=(d-grid31(k,itype0))/(grid31(k+2,itype0)-grid31(k,itype0))
      y=(x-0.5d0)*pi2
      f1=0.5d0*(cos(y)+1)
      feat3_tmp(1,j,itype)=f1
      ind_f(1,j,itype,iat)=k+1

      y2=-pi*sin(y)/(d*(grid31(k+2,itype0)-grid31(k,itype0)))
      dfeat3_tmp(1,j,itype,:)=y2*dR_neigh(:,j,itype,iat)

      else
        
      feat3_tmp(1,j,itype)=0.d0
      ind_f(1,j,itype,iat)=1    ! a place holder, no effect
      dfeat3_tmp(1,j,itype,:)=0.d0
      endif

      if(k.gt.0) then
      x=(d-grid31(k-1,itype0))/(grid31(k+1,itype0)-grid31(k-1,itype0))
      y=(x-0.5d0)*pi2
      f1=0.5d0*(cos(y)+1)
      feat3_tmp(2,j,itype)=f1
      ind_f(2,j,itype,iat)=k

      y2=-pi*sin(y)/(d*(grid31(k+1,itype0)-grid31(k-1,itype0)))
      dfeat3_tmp(2,j,itype,:)=y2*dR_neigh(:,j,itype,iat)

      else
      feat3_tmp(2,j,itype)=0.d0
      ind_f(2,j,itype,iat)=1
      dfeat3_tmp(2,j,itype,:)=0.d0
      endif
!cccccccccccc So, one Rij will always have two features k, k+1  (1,2)
!cccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
1000  continue


!   Now, the three body feature
!ccccccccccccccccccccccccccccccccccccc



      do 2000 itype2=1,ntype
      do 2000 itype1=1,itype2

      itype12=itype1+((itype2-1)*itype2)/2


      do 2000 j2=1,num_neigh(itype2,iat)
      do 2000 j1=1,num_neigh(itype1,iat)

!      if(itype1.eq.itype2.and.j1.ge.j2) goto 2000
      if(itype1.eq.itype2.and.j1.eq.j2) goto 2000

      jj1=ind_all_neigh(j1,itype1,iat)
      jj2=ind_all_neigh(j2,itype2,iat)

      dd=(dR_neigh(1,j1,itype1,iat)-dR_neigh(1,j2,itype2,iat))**2+ &
         (dR_neigh(2,j1,itype1,iat)-dR_neigh(2,j2,itype2,iat))**2+ &
         (dR_neigh(3,j1,itype1,iat)-dR_neigh(3,j2,itype2,iat))**2

      d=dsqrt(dd)

!      if(d.gt.Rc2) goto 2000
      if(d.gt.Rc2(itype0).or.d.lt.1.D-4) goto 2000

      do k=1,n3b2(itype0)+1
      if(grid32(k,itype0).ge.d) exit
      enddo
      k=k-1

      if(k.gt.n3b2(itype0))  k=n3b2(itype0)


      if(k.lt.n3b2(itype0)) then
      x=(d-grid32(k,itype0))/(grid32(k+2,itype0)-grid32(k,itype0))
      y=(x-0.5d0)*pi2
      f1=0.5d0*(cos(y)+1)
      f32(1)=f1
      ind_f32(1)=k+1
      y2=-pi*sin(y)/(d*(grid32(k+2,itype0)-grid32(k,itype0)))
      df32(1,1,:)=y2*(dR_neigh(:,j1,itype1,iat)-dR_neigh(:,j2,itype2,iat))
      df32(1,2,:)=-df32(1,1,:)
      else
      f32(1)=0.d0
      ind_f32(1)=1
      df32(1,:,:)=0.d0
      endif

      if(k.gt.0) then
      x=(d-grid32(k-1,itype0))/(grid32(k+1,itype0)-grid32(k-1,itype0))
      y=(x-0.5d0)*pi2
      f1=0.5d0*(cos(y)+1)
      f32(2)=f1
      ind_f32(2)=k
      y2=-pi*sin(y)/(d*(grid32(k+1,itype0)-grid32(k-1,itype0)))
      df32(2,1,:)=y2*(dR_neigh(:,j1,itype1,iat)-dR_neigh(:,j2,itype2,iat))
      df32(2,2,:)=-df32(2,1,:)

      else
      f32(2)=0.d0
      ind_f32(2)=1
      df32(2,:,:)=0.d0
      endif


!cccccccccccccccccccccccc
!   Each R has two k features, so for the three R, we have the following
      do i1=1,2
      do i2=1,2
      do j12=1,2
      k1=ind_f(i1,j1,itype1,iat)
      k2=ind_f(i2,j2,itype2,iat)
      k12=ind_f32(j12)

      ii_f=0
      if(itype1.ne.itype2) then
      ii_f=k1+(k2-1)*n3b1(itype0)+(k12-1)*n3b1(itype0)**2
      endif
      if(itype1.eq.itype2.and.k1.le.k2) then
      ii_f=k1+((k2-1)*k2)/2+(k12-1)*(n3b1(itype0)*(n3b1(itype0)+1))/2
      endif

      if(ii_f.ne.0) then
      feat3(ii_f,itype12,iat)=feat3(ii_f,itype12,iat)+ &
       feat3_tmp(i1,j1,itype1)*feat3_tmp(i2,j2,itype2)*f32(j12)

      dfeat3(ii_f,itype12,iat,jj1,:)=dfeat3(ii_f,itype12,iat,jj1,:)+ &
        dfeat3_tmp(i1,j1,itype1,:)*feat3_tmp(i2,j2,itype2)*f32(j12)+ &
        feat3_tmp(i1,j1,itype1)*feat3_tmp(i2,j2,itype2)*df32(j12,1,:)

      dfeat3(ii_f,itype12,iat,jj2,:)=dfeat3(ii_f,itype12,iat,jj2,:)+ &
        feat3_tmp(i1,j1,itype1)*dfeat3_tmp(i2,j2,itype2,:)*f32(j12)+ &
        feat3_tmp(i1,j1,itype1)*feat3_tmp(i2,j2,itype2)*df32(j12,2,:)

      dfeat3(ii_f,itype12,iat,1,:)=dfeat3(ii_f,itype12,iat,1,:)- &
        dfeat3_tmp(i1,j1,itype1,:)*feat3_tmp(i2,j2,itype2)*f32(j12)- &
        feat3_tmp(i1,j1,itype1)*dfeat3_tmp(i2,j2,itype2,:)*f32(j12) 

!cccc (ii_f,itype12) is the feature index
      endif

      enddo
      enddo
      enddo
2000   continue


3000   continue

!cccccccccccccccccccccccccccccccccccccccccccccccc
!cccccccccccccccccccccccccccccccccccccccccccccccc
!   Now, we collect everything together, collapse the index (k,itype)
!   and feat2,feat3, into a single feature. 

      do 5000 iat=1,natom
      itype0=itype_atom(iat)
      nneigh=num_neigh_alltype(iat)

      num=0

      do itype2=1,ntype
      do itype1=1,itype2

      itype12=itype1+((itype2-1)*itype2)/2

      do k1=1,n3b1(itype0)
      do k2=1,n3b1(itype0)
      do k12=1,n3b2(itype0)

      ii_f=0
      if(itype1.ne.itype2) then
      ii_f=k1+(k2-1)*n3b1(itype0)+(k12-1)*n3b1(itype0)**2
      endif
      if(itype1.eq.itype2.and.k1.le.k2) then
      ii_f=k1+((k2-1)*k2)/2+(k12-1)*(n3b1(itype0)*(n3b1(itype0)+1))/2
      endif

      if(ii_f.gt.0) then
      num=num+1
      feat_all(num,iat)=feat3(ii_f,itype12,iat)
      if (abs(feat_all(num,iat)).lt.1E-38) then
            feat_all(num,iat)=0.d0
            endif
      dfeat_all(num,iat,1:nneigh,:)=dfeat3(ii_f,itype12,iat,1:nneigh,:)
      endif

      enddo
      enddo
      enddo
      enddo
      enddo
      nfeat_atom(iat)=num
      if(num.gt.nfeat0m) then
      write(6,*) "num.gt.nfeat0m,stop",num,nfeat0m
      stop
      endif

5000  continue


!ccccccccccccccccccccccccccccccccccc
!  Now, we have to redefine the dfeat_all in another way. 
!  dfeat_all(i,iat,jneigh,3) means:
!  d_ith_feat_of_iat/d_R(jth_neigh_of_iat)
!  dfeat_allR(i,iat,jneigh,3) means:
!  d_ith_feat_of_jth_neigh/d_R(iat)
!cccccccccccccccccccccccccccccccccccccc
      dfeat_allR=0.d0

      do iat=1,natom
      do j=1,num_neigh_alltype(iat)
!ccccccccccccccccccc, this include the one which is itself, j=1

      iat2=list_neigh_alltype(j,iat)

      do j2=1,num_neigh_alltype(iat2)
      if(list_neigh_alltype(j2,iat2).eq.iat) then
      dd=(dR_neigh_alltype(1,j,iat)+dR_neigh_alltype(1,j2,iat2))**2+  &
         (dR_neigh_alltype(2,j,iat)+dR_neigh_alltype(2,j2,iat2))**2+  &
         (dR_neigh_alltype(3,j,iat)+dR_neigh_alltype(3,j2,iat2))**2  

      if(dd.lt.1.E-8) then
 
      do ii_f=1,nfeat_atom(iat)
      dfeat_allR(ii_f,iat2,j2,:)=dfeat_all(ii_f,iat,j,:)
!ccc Note, dfeat_allR(i,iat2,j2,3), it can have more i then nfeat_atom(iat2), 
! since it is the nfeat of j2_neighbore
      enddo
      endif
      endif

      enddo

      enddo
      enddo
!ccccccccccccccccccccccccccccccccccccc

      return
      end subroutine find_feature_3b_type1



