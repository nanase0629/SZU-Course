import java.util.Arrays;
import java.util.TreeMap;
import java.util.Scanner;
import java.util.*;
class Team2 implements Comparable<Team2>
{
    public String name;
    public int Gold,Silver,Bronze;
    public Team2(String name,int gold,int silver,int bronze){
        this.name=name;
        this.Gold=gold;
        this.Silver=silver;
        this.Bronze=bronze;
    }
    @Override
    public String toString(){
        return name+" "+Gold+" "+Silver+" "+Bronze;
    }

    @Override
    public int compareTo(Team2 t){
        if(this.Silver>t.Silver)return 1;
        else if(this.Silver<t.Silver)return -1;
        return 0;
    }

}
public class Main2 {
    public static void main(String[]args){
        TreeMap<Team2,String>teams2=new TreeMap<>();
        teams2.put(new Team2("CHN", 201, 111, 71),"CHN");
        teams2.put( new Team2("JPN", 52, 67, 69),"JPN");
        teams2.put( new Team2("KOR", 42, 59, 89),"KOR");
        teams2.put( new Team2("IND", 28, 38, 41),"IND");
        teams2.put( new Team2("UZB", 22, 18, 31),"UZB");
        teams2.put( new Team2("TPE", 19, 20, 28),"TPE");
        teams2.put( new Team2("IRI", 13, 21, 20),"IRI");
        teams2.put( new Team2("THA", 12, 14, 32),"THA");
        teams2.put( new Team2("BRN", 12, 3, 5),"BRN");
        teams2.put( new Team2("PRK", 11, 18, 10),"PRK");
        System.out.println("使用Comparable接口");
        System.out.println("按照银牌数量从小到大排序的队伍信息：");
        for(String s: teams2.values()){
            System.out.println(s);
        }
    }

}
