from django.db import models

from django.db.models import Avg, Max, Min

from django.db.models import Q

from django.utils.dateparse import *

from django.core.exceptions import ValidationError

import copy


# Create your models here.
class AnneeScolaire(models.Model):
  
    nom = models.CharField(max_length=200)
    anneescolaire = models.IntegerField(default=0)    
    def __str__(self):
        return self.nom

class Diplome(models.Model):  #Author
    nom = models.CharField(max_length=200)     
    anneescolaire = models.ForeignKey(AnneeScolaire, on_delete=models.PROTECT)   
    def __str__(self):
        return self.nom +" "+self.anneescolaire.nom
    def get_eleves(self):
        return FiliereEleve.objects.filter(filiere__diplome__id=self.id)
    def get_periodes(self):
        return Periode.objects.filter(diplome__id=self.id).all()
    def get_filieres(self):
        return Filiere.objects.filter(diplome__id=self.id).all()


class Filiere(models.Model):  #Author
    nom = models.CharField(max_length=200)     
    diplome = models.ForeignKey(Diplome, on_delete=models.PROTECT)   
    def __str__(self):
        return self.diplome.nom +" "+self.nom+" ("+self.diplome.anneescolaire.nom+")"
    def nommodele(self):
        return 'filiere '+str(self.nom)
    def nommodeledb(self):
        return 'filiere/'+str(self.id)
    
 #BookFormSet = inlineformset_factory(Diplome, Periode, fields=('title',))
# author = Author.objects.get(name='Mike Royko')
#formset = BookFormSet(instance=author)

class Periode(models.Model): #Book
  
    nom = models.CharField(max_length=200)
    diplome= models.ForeignKey(Diplome, on_delete=models.PROTECT) 
    datedebut=models.DateTimeField()
    datefin=models.DateTimeField()  
    def __str__(self):
        return self.diplome.nom+" "+self.nom +" "+self.diplome.anneescolaire.nom
    def nommodele(self):
        return 'Période'

class Personne(models.Model):
    nom = models.CharField(max_length=200)
    prenom = models.CharField(max_length=200)
    email = models.CharField(max_length=200,null=True, blank=True)
    
class Adresse(models.Model):
    
    pays= models.CharField(max_length=200)
    ville = models.CharField(max_length=200)
    adresse1= models.CharField(max_length=200) 
    adresse2= models.CharField(max_length=200,null=True, blank=True) 
    adresse3= models.CharField(max_length=200,null=True, blank=True)   
    personne=models.ForeignKey(Personne,on_delete=models.CASCADE)
    
    def nommodele(self):
        return 'Adresse'
    
     
class Eleve(Personne):
    filiere = models.ManyToManyField(Filiere, through="FiliereEleve")
    def __str__(self):
        lastannscodip=FiliereEleve.objects.filter(eleve__id=self.id ).all().aggregate(Max('filiere__diplome__anneescolaire'))
        lastdip=FiliereEleve.objects.filter(eleve__id=self.id ).filter(filiere__diplome__anneescolaire__id=lastannscodip['filiere__diplome__anneescolaire__max']).first()
        if lastdip: return self.nom+" "+self.prenom +" ("+ str(lastdip.filiere.diplome.nom)+" "+lastdip.filiere.diplome.anneescolaire.nom+")"
        else : return " Aucune formation "
    def get_groupes(self):
        res="";
        for p in Inscription.objects.filter(eleve__id=self.id).all() :
            res=res+p.groupe.ue.nom +" ("+p.groupe.nom+"), "
        return res  
    def get_diplomes(self):
        res=""
        for d in FiliereEleve.objects.filter(eleve__id=self.id ).all():  
             res=res+"---"+d.filiere.diplome.nom +"  "+d.filiere.diplome.anneescolaire.nom
        return res   
    def nommodeledb(self):
        return 'Eleve'
    def get_last_diplome(self):
        #lastdip=DiplomeEleve.objects.filter(eleve__id=self.id ).all().aggregate(Max('diplome__anneescolaire'))
       #
       #
       #
        lastannscodip=FiliereEleve.objects.filter(eleve__id=self.id ).all().aggregate(Max('filiere__diplome__anneescolaire'))
        lastdip=FiliereEleve.objects.filter(eleve__id=self.id ).filter(filiere__diplome__anneescolaire__id=lastannscodip['filiere__diplome__anneescolaire__max']).first()
        if lastdip: return str(lastdip.filiere.diplome.nom)+" "+lastdip.filiere.diplome.anneescolaire.nom
        else : return " Aucune formation "
                

class FiliereEleve(models.Model):  
    filiere=models.ForeignKey(Filiere,on_delete=models.CASCADE)
    eleve=models.ForeignKey(Eleve,on_delete=models.CASCADE)
    def nommodele(self):
        return 'filiere '+str(self.filiere.nom)
    def nommodeledb(self):
        return 'eleve/'+str(self.eleve.id)
    def nommodeledb2(self):
        return 'filiere/'+str(self.filiere.id)

        
class Enseignant(Personne):
    def __str__(self):
        return self.nom
    def get_groupes(self):
        res="";
        for p in Groupe.objects.filter(enseignants__id=self.id).all() :
            res=res+p.ue.nom +" ("+p.nom+"), "
        return res

class UE(models.Model):  
    nom = models.CharField(max_length=200)     
    descriptif = models.CharField(max_length=200,null=True, blank=True)     
    periode = models.ForeignKey(Periode, on_delete=models.PROTECT) 
    filieres= models.ManyToManyField(Filiere,through="UEFilieres")
    def __str__(self):
        return self.nom+" ("+self.periode.diplome.nom+" "+self.periode.diplome.anneescolaire.nom+")"
    def get_groupes(self):
        res="";
        for p in Groupe.objects.filter(ue__id=self.id).all() :
            res=res+", "+ p.nom
        return res

class UEFilieres(models.Model):  
    ue=models.ForeignKey(UE,on_delete=models.CASCADE);
    filiere=models.ForeignKey(Filiere,on_delete=models.CASCADE);
    

class Groupe(models.Model):  
    nom = models.CharField(max_length=200)     
    ue = models.ForeignKey(UE, on_delete=models.CASCADE) 
    enseignants= models.ManyToManyField(Enseignant, through="GroupesEnseignants")
    def __str__(self):
        return self.ue.nom +" "+self.nom+" ("+self.ue.periode.diplome.nom+" "+ self.ue.periode.diplome.anneescolaire.nom+")"
    def get_nb_eleves(self):
        return Inscription.objects.filter(groupe__id=self.id).count()
    def nommodeledb(self):
        return 'groupe/'+str(self.id)
    
    
class GroupesEnseignants(models.Model):  
    groupe=models.ForeignKey(Groupe,on_delete=models.PROTECT)
    enseignant=models.ForeignKey(Enseignant,on_delete=models.PROTECT)
    def nommodele(self):
        return 'groupe'
    def nommodeledb(self):
        return 'groupe/'+str(self.groupe.id)
    def nommodeledb2(self):
        return 'enseignant/'+str(self.enseignant.id)
    def __str__(self): 
         return self.groupe.nom+" "+str(self.groupe.ue)

class Inscription(models.Model):  
    groupe = models.ForeignKey(Groupe, on_delete=models.PROTECT) 
    eleve = models.ForeignKey(Eleve, on_delete=models.PROTECT) 
   # enseignant= models.ForeignKey(Enseignant, on_delete=models.PROTECT) 
    def __str__(self):
        return self.groupe.ue.nom+" "+self.groupe.nom
    def nommodele(self):
        return 'inscription '+str(self.groupe.ue.periode.diplome.anneescolaire)
    def nommodeledb(self):
        return 'eleve/'+str(self.eleve.id)
    def nommodeledb2(self):
        return 'groupe/'+str(self.groupe.id)

class Salle(models.Model):  
    nom = models.CharField(max_length=200)
    batiment = models.CharField(max_length=200,null=True, blank=True)     
    capacite = models.IntegerField(default=0)     
    def __str__(self):
        return self.nom

class Cours(models.Model):  
    groupes = models.ManyToManyField(Groupe, through="CoursGroupes")
    salles= models.ManyToManyField(Salle,through="CoursSalles")
    datedebut=models.DateTimeField()
    datefin=models.DateTimeField()
    def __str__(self): 
        str="";  
        str=str+" groupes :"     
        for eg in self.groupes.all() :
            str=str+eg.ue.nom +" "+eg.nom
            str=str+" "
        str=str+" salle :"
        for es in self.salles.all() :
            str=str+es.nom
        str=str+" "+self.datedebut.strftime('%Y-%m-%d %H:%M')+"\r\n "+self.datefin.strftime('%Y-%m-%d %H:%M')
        return str
               
    def verifResaSalle(self):
        datedebutcours=self.datedebut
        datefincours=self.datefin
        pb=False
        messerror='';
        for ts in self.salles.all():
            for c in CoursSalles.objects.filter( Q(salle__id=ts.id)).all() :             
              if self.id != c.cours.id :                     
                        if ((c.cours.datedebut>=datedebutcours and c.cours.datedebut<datefincours) or
                            (c.cours.datefin <=datefincours and c.cours.datefin>datedebutcours ) or 
                            (c.cours.datedebut<=datedebutcours and c.cours.datefin>=datefincours)) :
                                pb=True
                                #messerror=" chevauchement :"+str(c.cours)
                                messerror=" oldcours "+str(c.cours)
        if pb is True :        
            raise ValueError(messerror) 
        
    def save(self, *args, **kwargs):
        super(Cours, self).save(*args, **kwargs)
        self.verifResaSalle()

#
class CoursGroupes(models.Model):  
    cours=models.ForeignKey(Cours,on_delete=models.CASCADE);
    groupe=models.ForeignKey(Groupe,on_delete=models.CASCADE);
    
class CoursSalles(models.Model):  
    cours=models.ForeignKey(Cours,on_delete=models.CASCADE);
    salle=models.ForeignKey(Salle,on_delete=models.CASCADE);